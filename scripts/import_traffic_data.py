"""
scripts/import_traffic_data.py
================================
SignalAI – Traffic Data Import Script

Reads the cleaned CSV and inserts records into the PostgreSQL
traffic_records table via SQLAlchemy.

Features:
  - Reads DATABASE_URL from .env (no hardcoded credentials)
  - Builds junction_code → junction_id lookup from live DB
  - Skips duplicate (junction_id, recorded_at) pairs
  - Validates every row before insert
  - Inserts in configurable batches (default: 500)
  - Shows progress every batch
  - Reports inserted / skipped / failed counts
  - Uses transactions (batch-level rollback on error)

Usage (from project root, with backend venv active):
    cd "/Users/sahilp4514/Desktop/mini project/all code file/backend"
    source venv/bin/activate
    cd ..
    python3 scripts/import_traffic_data.py

Prerequisites:
    - Cleaned CSV exists: data/processed/traffic_records_cleaned.csv
    - backend/.env has correct DATABASE_URL
    - PostgreSQL is running
    - signalai database has all tables
"""

import csv
import os
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# Allow imports from backend/app without installing as a package
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR  = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Load .env from backend/.env before importing database module
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("import_traffic")

# ── Configuration ──────────────────────────────────────────────────────────────

CLEAN_CSV   = PROJECT_ROOT / "data" / "processed" / "traffic_records_cleaned.csv"
BATCH_SIZE  = 500   # rows per commit batch

VALID_LEVELS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}

# IST offset (UTC+5:30) — dataset timestamps are treated as local IST time
IST = timezone(timedelta(hours=5, minutes=30))


# ── Database connection ────────────────────────────────────────────────────────

def get_engine():
    """Create SQLAlchemy engine from DATABASE_URL environment variable."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        log.error("DATABASE_URL not found. Ensure backend/.env is configured.")
        sys.exit(1)
    log.info(f"Connecting to: {db_url.split('@')[-1]}")   # hide credentials
    return create_engine(db_url, pool_pre_ping=True, echo=False)


# ── Junction lookup ────────────────────────────────────────────────────────────

def build_junction_lookup(session: Session) -> dict[str, int]:
    """
    Fetch all junctions from the DB and build a dict:
        junction_code (e.g. 'J-101') → id (integer)
    """
    rows = session.execute(
        text("SELECT junction_code, id FROM junctions")
    ).fetchall()
    lookup = {row[0]: row[1] for row in rows}
    log.info(f"Loaded {len(lookup)} junctions from DB: {sorted(lookup.keys())}")
    return lookup


# ── Existing record lookup ──────────────────────────────────────────────────────

def build_existing_keys(session: Session) -> set[tuple[int, str]]:
    """
    Load existing (junction_id, recorded_at) pairs from DB to prevent duplicates.
    Returns a set of (junction_id_int, timestamp_str) tuples.
    """
    log.info("Loading existing traffic_records to detect duplicates...")
    rows = session.execute(
        text("SELECT junction_id, recorded_at::text FROM traffic_records")
    ).fetchall()
    # Store as (int, ISO-string without microseconds for comparison)
    existing = set()
    for junc_id, ts_raw in rows:
        # PostgreSQL returns timestamptz as ISO string
        # Normalize to "YYYY-MM-DD HH:MM:SS" for comparison
        ts_norm = ts_raw[:19].replace("T", " ")
        existing.add((junc_id, ts_norm))
    log.info(f"Found {len(existing):,} existing records in traffic_records.")
    return existing


# ── Row validation ─────────────────────────────────────────────────────────────

def validate_and_transform(row: dict, junction_lookup: dict) -> dict | None:
    """
    Validate and transform a single CSV row.
    Returns a dict ready for DB insert, or None if invalid.
    """
    junction_code = row.get("junction_id", "").strip().upper()
    junction_id   = junction_lookup.get(junction_code)
    if junction_id is None:
        return None   # unknown junction — skip silently

    ts_raw = row.get("timestamp", "").strip()
    try:
        ts_naive = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S")
        ts_aware = ts_naive.replace(tzinfo=IST)
    except (ValueError, TypeError):
        return None

    # vehicle_count (nullable)
    vc_raw = row.get("vehicle_count", "").strip()
    vehicles = None
    if vc_raw:
        try:
            v = int(vc_raw)
            vehicles = v if v >= 0 else None
        except ValueError:
            vehicles = None

    # congestion_pct (nullable)
    cg_raw = row.get("congestion_pct", "").strip()
    congestion = None
    if cg_raw:
        try:
            c = int(cg_raw)
            congestion = c if 0 <= c <= 100 else None
        except ValueError:
            congestion = None

    # traffic_level
    level = row.get("traffic_level", "").strip().upper()
    if level not in VALID_LEVELS:
        return None

    return {
        "junction_id":          junction_id,
        "recorded_at":          ts_aware,
        "vehicles":             vehicles,
        "traffic_level":        level,
        "congestion_percentage": congestion,
    }


# ── Import ─────────────────────────────────────────────────────────────────────

def import_traffic_records(session: Session, junction_lookup: dict) -> dict:
    """
    Main import function. Reads cleaned CSV and inserts into traffic_records.
    Returns stats dict.
    """
    if not CLEAN_CSV.exists():
        log.error(f"Cleaned CSV not found: {CLEAN_CSV}")
        log.error("Run: python3 scripts/prepare_traffic_data.py first")
        sys.exit(1)

    existing_keys = build_existing_keys(session)

    stats = {
        "total_read":    0,
        "inserted":      0,
        "skipped_dup":   0,
        "skipped_invalid": 0,
        "failed":        0,
    }

    batch = []
    start_time = time.time()

    log.info(f"Reading cleaned CSV: {CLEAN_CSV}")
    with open(CLEAN_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats["total_read"] += 1

            record = validate_and_transform(row, junction_lookup)
            if record is None:
                stats["skipped_invalid"] += 1
                continue

            # Duplicate detection
            ts_norm = record["recorded_at"].strftime("%Y-%m-%d %H:%M:%S")
            dedup_key = (record["junction_id"], ts_norm)
            if dedup_key in existing_keys:
                stats["skipped_dup"] += 1
                continue

            existing_keys.add(dedup_key)   # mark as seen for in-batch dedup
            batch.append(record)

            # ── Batch insert ───────────────────────────────────────────────
            if len(batch) >= BATCH_SIZE:
                inserted, failed = flush_batch(session, batch)
                stats["inserted"] += inserted
                stats["failed"]   += failed
                batch = []

                elapsed = time.time() - start_time
                log.info(
                    f"  Progress: {stats['total_read']:>6,} read | "
                    f"{stats['inserted']:>6,} inserted | "
                    f"{stats['skipped_dup']:>5,} dup | "
                    f"{elapsed:.1f}s"
                )

    # Flush remaining rows
    if batch:
        inserted, failed = flush_batch(session, batch)
        stats["inserted"] += inserted
        stats["failed"]   += failed

    stats["elapsed_seconds"] = round(time.time() - start_time, 2)
    return stats


def flush_batch(session: Session, batch: list[dict]) -> tuple[int, int]:
    """
    Insert one batch of records using a raw parameterized INSERT.
    Returns (inserted_count, failed_count).
    """
    try:
        session.execute(
            text("""
                INSERT INTO traffic_records
                    (junction_id, recorded_at, vehicles, traffic_level, congestion_percentage)
                VALUES
                    (:junction_id, :recorded_at, :vehicles, :traffic_level, :congestion_percentage)
            """),
            batch,
        )
        session.commit()
        return len(batch), 0
    except SQLAlchemyError as exc:
        session.rollback()
        log.error(f"Batch insert failed: {exc}")
        return 0, len(batch)


# ── Post-import verification ────────────────────────────────────────────────────

def verify_import(session: Session) -> dict:
    """Run SQL queries to verify the imported data."""
    results = {}

    row = session.execute(
        text("SELECT COUNT(*) FROM traffic_records")
    ).fetchone()
    results["total_count"] = row[0]

    row = session.execute(
        text("SELECT MIN(recorded_at), MAX(recorded_at) FROM traffic_records")
    ).fetchone()
    results["earliest"] = str(row[0])
    results["latest"]   = str(row[1])

    row = session.execute(
        text("SELECT MIN(vehicles), MAX(vehicles), MIN(congestion_percentage), MAX(congestion_percentage) FROM traffic_records")
    ).fetchone()
    results["min_vehicles"]   = row[0]
    results["max_vehicles"]   = row[1]
    results["min_congestion"] = row[2]
    results["max_congestion"] = row[3]

    rows = session.execute(
        text("""
            SELECT j.junction_code, COUNT(*) as cnt
            FROM traffic_records tr
            JOIN junctions j ON j.id = tr.junction_id
            GROUP BY j.junction_code
            ORDER BY j.junction_code
        """)
    ).fetchall()
    results["per_junction"] = {r[0]: r[1] for r in rows}

    rows = session.execute(
        text("""
            SELECT traffic_level, COUNT(*) as cnt
            FROM traffic_records
            GROUP BY traffic_level
            ORDER BY traffic_level
        """)
    ).fetchall()
    results["per_level"] = {r[0]: r[1] for r in rows}

    rows = session.execute(
        text("""
            SELECT COUNT(*) FROM traffic_records
            WHERE vehicles IS NULL OR congestion_percentage IS NULL
        """)
    ).fetchone()
    results["null_count"] = rows[0]

    return results


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    engine  = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Pre-import count
        pre_count = session.execute(
            text("SELECT COUNT(*) FROM traffic_records")
        ).fetchone()[0]
        log.info(f"Pre-import traffic_records count: {pre_count:,}")

        # Build junction lookup
        junction_lookup = build_junction_lookup(session)

        # Run import
        log.info(f"Starting import (batch size: {BATCH_SIZE})...")
        stats = import_traffic_records(session, junction_lookup)

        # Post-import verification
        log.info("Running post-import verification...")
        verify = verify_import(session)

        # ── Print full report ──────────────────────────────────────────────
        print()
        print("=" * 60)
        print("  IMPORT COMPLETE — SIGNALAI TRAFFIC RECORDS")
        print("=" * 60)
        print(f"  Pre-import count   : {pre_count:,}")
        print(f"  CSV rows read      : {stats['total_read']:,}")
        print(f"  Rows inserted      : {stats['inserted']:,}")
        print(f"  Skipped (duplicate): {stats['skipped_dup']:,}")
        print(f"  Skipped (invalid)  : {stats['skipped_invalid']:,}")
        print(f"  Failed (DB error)  : {stats['failed']:,}")
        print(f"  Total time         : {stats['elapsed_seconds']}s")
        print(f"  Post-import count  : {verify['total_count']:,}")
        print()
        print("  Timestamp range:")
        print(f"    Earliest : {verify['earliest']}")
        print(f"    Latest   : {verify['latest']}")
        print()
        print("  Value ranges:")
        print(f"    Vehicles    : {verify['min_vehicles']} – {verify['max_vehicles']}")
        print(f"    Congestion  : {verify['min_congestion']} – {verify['max_congestion']}%")
        print(f"    NULL rows   : {verify['null_count']:,}")
        print()
        print("  Records per junction:")
        for code, cnt in verify["per_junction"].items():
            print(f"    {code} : {cnt:,}")
        print()
        print("  Records per traffic level:")
        for lvl, cnt in verify["per_level"].items():
            print(f"    {lvl:<10} : {cnt:,}")
        print("=" * 60)

    except Exception as exc:
        log.error(f"Import failed: {exc}", exc_info=True)
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
