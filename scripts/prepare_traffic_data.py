"""
scripts/prepare_traffic_data.py
=================================
SignalAI – Data Cleaning & Preparation Script

Reads the raw Kaggle traffic CSV, applies cleaning rules, validates every
row, and writes a clean CSV ready for database import.

Cleaning steps:
  1. Normalize column names (lowercase, strip whitespace)
  2. Parse and validate timestamps
  3. Cast numeric fields (vehicle_count, congestion_pct)
  4. Validate ranges (congestion 0–100, vehicles >= 0)
  5. Validate traffic_level enum values
  6. Handle missing values (set to NULL/empty)
  7. Reject structurally invalid rows
  8. Remove exact duplicate (junction_id, timestamp) pairs
  9. Write cleaned CSV
  10. Print cleaning report

Usage (from project root):
    python3 scripts/prepare_traffic_data.py

Output:
    data/processed/traffic_records_cleaned.csv
    data/DATA_CLEANING_REPORT.md
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV       = os.path.join(PROJECT_ROOT, "data", "raw",       "kaggle_traffic_dataset.csv")
CLEAN_CSV     = os.path.join(PROJECT_ROOT, "data", "processed", "traffic_records_cleaned.csv")
REPORT_PATH   = os.path.join(PROJECT_ROOT, "data",              "DATA_CLEANING_REPORT.md")

# ── Constants ─────────────────────────────────────────────────────────────────

TIMESTAMP_FORMAT     = "%Y-%m-%d %H:%M:%S"
VALID_TRAFFIC_LEVELS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
VALID_JUNCTION_IDS   = {"J-101", "J-102", "J-103", "J-104",
                        "J-105", "J-106", "J-107", "J-108"}

# ── Rejection reasons ─────────────────────────────────────────────────────────

REASON_MISSING_TIMESTAMP   = "missing or empty timestamp"
REASON_BAD_TIMESTAMP       = "timestamp does not match expected format"
REASON_MISSING_JUNCTION    = "missing or empty junction_id"
REASON_UNKNOWN_JUNCTION    = "junction_id not in known set"
REASON_MISSING_LEVEL       = "missing or empty traffic_level"
REASON_BAD_LEVEL           = "traffic_level not in valid enum"
REASON_NEGATIVE_VEHICLES   = "vehicle_count is negative"
REASON_BAD_CONGESTION      = "congestion_pct out of range (must be 0–100)"
REASON_DUPLICATE           = "duplicate (junction_id, timestamp) pair"


def parse_timestamp(raw: str) -> datetime | None:
    """Parse timestamp string. Returns datetime on success, None on failure."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, TIMESTAMP_FORMAT)
    except ValueError:
        return None


def parse_int_nullable(raw: str) -> tuple[int | None, bool]:
    """
    Parse an integer field that may be empty.
    Returns (value, is_valid) where:
      - (None, True)  → empty string, acceptable NULL
      - (int,  True)  → valid integer
      - (None, False) → non-numeric, invalid
    """
    raw = raw.strip()
    if not raw:
        return None, True       # acceptable NULL
    try:
        return int(raw), True
    except ValueError:
        return None, False      # non-numeric → reject


def clean_dataset(raw_csv: str) -> dict:
    """
    Main cleaning function. Reads the raw CSV and returns a dict with:
      - cleaned_rows: list of valid, clean row dicts
      - stats: detailed counters for the report
      - rejections: list of (row_num, row_dict, reason) for the report
    """
    stats = {
        "total_read":           0,
        "missing_timestamp":    0,
        "bad_timestamp":        0,
        "missing_junction":     0,
        "unknown_junction":     0,
        "missing_level":        0,
        "bad_level":            0,
        "negative_vehicles":    0,
        "bad_congestion":       0,
        "null_vehicles":        0,  # valid NULLs (not rejections)
        "null_congestion":      0,  # valid NULLs (not rejections)
        "duplicates_removed":   0,
        "total_rejected":       0,
        "total_cleaned":        0,
    }
    rejections  = []
    cleaned_rows = []
    seen_keys    = set()   # for duplicate detection: (junction_id, timestamp_str)

    print(f"Reading: {raw_csv}")
    with open(raw_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize column names
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

        for row_num, row in enumerate(reader, start=2):   # start=2: header is row 1
            stats["total_read"] += 1

            # ── 1. Timestamp ─────────────────────────────────────────────────
            raw_ts = row.get("timestamp", "").strip()
            if not raw_ts:
                stats["missing_timestamp"] += 1
                stats["total_rejected"]    += 1
                rejections.append((row_num, row, REASON_MISSING_TIMESTAMP))
                continue

            ts = parse_timestamp(raw_ts)
            if ts is None:
                stats["bad_timestamp"]   += 1
                stats["total_rejected"]  += 1
                rejections.append((row_num, row, REASON_BAD_TIMESTAMP))
                continue

            ts_str = ts.strftime(TIMESTAMP_FORMAT)   # normalized form

            # ── 2. Junction ID ────────────────────────────────────────────────
            junction_id = row.get("junction_id", "").strip().upper()
            if not junction_id:
                stats["missing_junction"] += 1
                stats["total_rejected"]   += 1
                rejections.append((row_num, row, REASON_MISSING_JUNCTION))
                continue

            if junction_id not in VALID_JUNCTION_IDS:
                stats["unknown_junction"] += 1
                stats["total_rejected"]   += 1
                rejections.append((row_num, row, REASON_UNKNOWN_JUNCTION))
                continue

            # ── 3. Traffic level ──────────────────────────────────────────────
            level = row.get("traffic_level", "").strip().upper()
            if not level:
                stats["missing_level"]   += 1
                stats["total_rejected"]  += 1
                rejections.append((row_num, row, REASON_MISSING_LEVEL))
                continue

            if level not in VALID_TRAFFIC_LEVELS:
                stats["bad_level"]       += 1
                stats["total_rejected"]  += 1
                rejections.append((row_num, row, REASON_BAD_LEVEL))
                continue

            # ── 4. Vehicle count (nullable) ───────────────────────────────────
            vehicles, v_valid = parse_int_nullable(row.get("vehicle_count", ""))
            if not v_valid:
                # Non-numeric string — treat as NULL rather than reject
                vehicles = None
                stats["null_vehicles"] += 1
            elif vehicles is not None and vehicles < 0:
                stats["negative_vehicles"] += 1
                stats["total_rejected"]    += 1
                rejections.append((row_num, row, REASON_NEGATIVE_VEHICLES))
                continue
            elif vehicles is None:
                stats["null_vehicles"] += 1

            # ── 5. Congestion percentage (nullable) ───────────────────────────
            congestion, c_valid = parse_int_nullable(row.get("congestion_pct", ""))
            if not c_valid:
                congestion = None
                stats["null_congestion"] += 1
            elif congestion is not None and not (0 <= congestion <= 100):
                stats["bad_congestion"]  += 1
                stats["total_rejected"]  += 1
                rejections.append((row_num, row, REASON_BAD_CONGESTION))
                continue
            elif congestion is None:
                stats["null_congestion"] += 1

            # ── 6. Duplicate detection ────────────────────────────────────────
            dedup_key = (junction_id, ts_str)
            if dedup_key in seen_keys:
                stats["duplicates_removed"] += 1
                stats["total_rejected"]     += 1
                rejections.append((row_num, row, REASON_DUPLICATE))
                continue

            seen_keys.add(dedup_key)

            # ── 7. Build clean row ────────────────────────────────────────────
            cleaned_rows.append({
                "timestamp":        ts_str,
                "junction_id":      junction_id,
                "vehicle_count":    "" if vehicles is None else str(vehicles),
                "congestion_pct":   "" if congestion is None else str(congestion),
                "traffic_level":    level,
            })

    stats["total_cleaned"] = len(cleaned_rows)
    return {"cleaned_rows": cleaned_rows, "stats": stats, "rejections": rejections}


def write_cleaned_csv(cleaned_rows: list[dict], output_path: str):
    """Write the cleaned rows to the output CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = ["timestamp", "junction_id", "vehicle_count", "congestion_pct", "traffic_level"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    print(f"✓ Cleaned CSV written: {output_path}")


def write_cleaning_report(stats: dict, rejections: list, report_path: str):
    """Write the DATA_CLEANING_REPORT.md file."""
    rejection_summary = defaultdict(int)
    for _, _, reason in rejections:
        rejection_summary[reason] += 1

    total = stats["total_read"]
    cleaned = stats["total_cleaned"]
    rejected = stats["total_rejected"]

    lines = [
        "# Data Cleaning Report",
        "## SignalAI – Traffic Dataset Preparation",
        "",
        f"**Script:** `scripts/prepare_traffic_data.py`  ",
        f"**Input:**  `data/raw/kaggle_traffic_dataset.csv`  ",
        f"**Output:** `data/processed/traffic_records_cleaned.csv`  ",
        f"**Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Original rows (excl. header) | {total:,} |",
        f"| Rows passed cleaning | {cleaned:,} |",
        f"| Rows rejected (total) | {rejected:,} |",
        f"| Rejection rate | {rejected/total*100:.2f}% |",
        f"| Valid NULL vehicle_count | {stats['null_vehicles']:,} |",
        f"| Valid NULL congestion_pct | {stats['null_congestion']:,} |",
        f"| Duplicate (junction,timestamp) pairs removed | {stats['duplicates_removed']:,} |",
        "",
        "---",
        "",
        "## Rejection Breakdown",
        "",
        "| Rejection Reason | Count |",
        "|---|---|",
    ]

    for reason, count in sorted(rejection_summary.items(), key=lambda x: -x[1]):
        lines.append(f"| {reason} | {count:,} |")

    lines += [
        "",
        "---",
        "",
        "## Transformations Applied",
        "",
        "| Step | Action |",
        "|---|---|",
        "| Column normalization | All column names lowercased and stripped |",
        "| Timestamp parsing | Parsed from `YYYY-MM-DD HH:MM:SS` format |",
        "| junction_id normalization | Uppercased before lookup |",
        "| traffic_level normalization | Uppercased for enum match |",
        "| vehicle_count empty → NULL | Stored as empty string in CSV → NULL in DB |",
        "| congestion_pct empty → NULL | Stored as empty string in CSV → NULL in DB |",
        "| Duplicate removal | One row kept per (junction_id, timestamp) pair |",
        "",
        "---",
        "",
        "## Validation Rules Applied",
        "",
        "| Field | Rule | Action on Violation |",
        "|---|---|---|",
        "| `timestamp` | Must be non-empty and match `YYYY-MM-DD HH:MM:SS` | REJECT row |",
        "| `junction_id` | Must be non-empty and in known set (J-101 to J-108) | REJECT row |",
        "| `traffic_level` | Must match LOW/MODERATE/HIGH/CRITICAL | REJECT row |",
        "| `vehicle_count` | If present, must be integer >= 0 | REJECT if negative |",
        "| `congestion_pct` | If present, must be integer 0–100 | REJECT if out of range |",
        "| `(junction_id, timestamp)` | Must be unique | REJECT duplicate |",
        "",
        "---",
        "",
        "## Columns Removed in Cleaned Output",
        "",
        "The following columns from the raw CSV were dropped (not needed in DB):",
        "",
        "| Column | Reason |",
        "|---|---|",
        "| `location_name` | Redundant — already in `junctions.name` |",
        "| `weather_condition` | Not in `traffic_records` schema |",
        "| `day_of_week` | Derivable from timestamp |",
        "| `is_weekend` | Derivable from timestamp |",
        "| `hour_of_day` | Derivable from timestamp |",
        "",
        "---",
        "",
        "## Cleaned Output Columns",
        "",
        "| Column | Maps to DB Field |",
        "|---|---|",
        "| `timestamp` | `recorded_at` |",
        "| `junction_id` | lookup → `junction_id` (FK integer) |",
        "| `vehicle_count` | `vehicles` |",
        "| `congestion_pct` | `congestion_percentage` |",
        "| `traffic_level` | `traffic_level` |",
    ]

    if rejections:
        lines += [
            "",
            "---",
            "",
            "## Sample Rejected Records (first 10)",
            "",
            "| Row # | junction_id | timestamp | Reason |",
            "|---|---|---|---|",
        ]
        for row_num, row, reason in rejections[:10]:
            jid = row.get("junction_id", "")[:10]
            ts  = row.get("timestamp",   "")[:20]
            lines.append(f"| {row_num} | {jid} | {ts} | {reason} |")

    report_text = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"✓ Cleaning report written: {report_path}")


def print_summary(stats: dict):
    """Print a human-readable summary to stdout."""
    print()
    print("=" * 55)
    print("  DATA CLEANING SUMMARY")
    print("=" * 55)
    print(f"  Total rows read     : {stats['total_read']:>7,}")
    print(f"  Rows cleaned/valid  : {stats['total_cleaned']:>7,}")
    print(f"  Rows rejected       : {stats['total_rejected']:>7,}")
    print(f"    · bad timestamp   : {stats['bad_timestamp']:>7,}")
    print(f"    · unknown junction: {stats['unknown_junction']:>7,}")
    print(f"    · bad level       : {stats['bad_level']:>7,}")
    print(f"    · negative vehicles: {stats['negative_vehicles']:>6,}")
    print(f"    · out-of-range congestion: {stats['bad_congestion']:>2,}")
    print(f"    · duplicates      : {stats['duplicates_removed']:>7,}")
    print(f"  Valid NULL vehicles : {stats['null_vehicles']:>7,}")
    print(f"  Valid NULL cong.    : {stats['null_congestion']:>7,}")
    print("=" * 55)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(RAW_CSV):
        print(f"ERROR: Raw CSV not found at {RAW_CSV}")
        print("Run: python3 scripts/generate_synthetic_dataset.py first")
        sys.exit(1)

    result       = clean_dataset(RAW_CSV)
    cleaned_rows = result["cleaned_rows"]
    stats        = result["stats"]
    rejections   = result["rejections"]

    write_cleaned_csv(cleaned_rows, CLEAN_CSV)
    write_cleaning_report(stats, rejections, REPORT_PATH)
    print_summary(stats)

    print(f"\nDone. {stats['total_cleaned']:,} clean rows ready for import.")
