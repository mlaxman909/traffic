"""
backend/import_vadodara_roads.py
=================================
Import Vadodara road network from OpenStreetMap GeoJSON into the road_network table.

Usage:
    cd backend
    source venv/bin/activate
    python import_vadodara_roads.py

    # Specify a custom GeoJSON path:
    python import_vadodara_roads.py --geojson /path/to/vadodara_road_network.geojson

    # Dry run (validate only, no DB write):
    python import_vadodara_roads.py --dry-run

DATA SOURCE:
    OpenStreetMap contributors (ODbL License)
    https://www.openstreetmap.org/copyright

IMPORTANT:
    This script imports GEOGRAPHIC ROAD NETWORK data only.
    It does NOT import traffic volume, congestion, or vehicle count data.
    OSM does not provide that information.

SAFETY:
    - Uses ON CONFLICT DO NOTHING (deduplicates by osm_id — safe to re-run)
    - Does NOT touch traffic_records, users, junctions, or any other table
    - Uses transactions — rolls back on error
    - Only imports LineString features (skips Polygon features)

GEOMETRY NOTE:
    PostGIS is not installed. Geometry stored as JSONB (GeoJSON geometry object).
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Make sure the backend package is importable ───────────────────────────────
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from sqlalchemy import text
from app.database import SessionLocal, get_settings
from app.models.road_network import RoadNetwork


# ── Default paths ─────────────────────────────────────────────────────────────

# Look for the GeoJSON in the project's data/ directory first, then Downloads
DEFAULT_PATHS = [
    script_dir.parent / "data" / "vadodara_road_network.geojson",
    Path.home() / "Downloads" / "vadodara_road_network.geojson",
]


# ── Haversine distance formula ────────────────────────────────────────────────

def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great-circle distance between two points (lon/lat in decimal degrees).
    Returns distance in metres.
    """
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def linestring_length_m(coordinates: list) -> float:
    """Calculate total length of a LineString in metres using haversine formula."""
    if len(coordinates) < 2:
        return 0.0
    total = 0.0
    for i in range(len(coordinates) - 1):
        lon1, lat1 = coordinates[i][0], coordinates[i][1]
        lon2, lat2 = coordinates[i + 1][0], coordinates[i + 1][1]
        total += haversine_m(lon1, lat1, lon2, lat2)
    return total


# ── Field parsers ─────────────────────────────────────────────────────────────

def parse_oneway(value) -> bool:
    """Parse OSM oneway tag to boolean. 'yes' → True, anything else → False."""
    if value is None:
        return False
    return str(value).strip().lower() == "yes"


def parse_bridge(value) -> bool:
    """Parse OSM bridge tag to boolean."""
    if value is None:
        return False
    return str(value).strip().lower() == "yes"


def parse_tunnel(value) -> bool:
    """Parse OSM tunnel tag to boolean."""
    if value is None:
        return False
    return str(value).strip().lower() == "yes"


def parse_lanes(value) -> int | None:
    """Parse OSM lanes tag to integer. Returns None if invalid."""
    if value is None:
        return None
    try:
        lanes = int(str(value).strip())
        return lanes if 1 <= lanes <= 20 else None
    except (ValueError, TypeError):
        return None


def parse_maxspeed(value) -> int | None:
    """
    Parse OSM maxspeed tag to integer (km/h).
    OSM values are strings like '60', '100', 'walk', 'none'.
    Returns None for non-numeric values.
    """
    if value is None:
        return None
    try:
        speed_str = str(value).strip().split()[0]  # e.g. "60 mph" → "60"
        speed = int(speed_str)
        return speed if 0 < speed <= 500 else None
    except (ValueError, TypeError, IndexError):
        return None


def parse_surface(value, max_len: int = 50) -> str | None:
    """Parse and truncate surface tag."""
    if value is None:
        return None
    s = str(value).strip()[:max_len]
    return s if s else None


def parse_road_name(value, max_len: int = 300) -> str | None:
    """Parse and truncate road name."""
    if value is None:
        return None
    s = str(value).strip()[:max_len]
    return s if s else None


def parse_ref(value, max_len: int = 50) -> str | None:
    """Parse and truncate road reference number."""
    if value is None:
        return None
    s = str(value).strip()[:max_len]
    return s if s else None


def parse_highway_type(value, max_len: int = 50) -> str | None:
    """Parse highway type — required field."""
    if value is None:
        return None
    s = str(value).strip()[:max_len]
    return s if s else None


# ── Feature validation ────────────────────────────────────────────────────────

def validate_feature(feature: dict, feature_index: int) -> tuple[bool, str]:
    """
    Validate a GeoJSON feature for import.
    Returns (is_valid, reason_if_invalid).
    """
    props = feature.get("properties") or {}
    geom = feature.get("geometry")

    # Must have geometry
    if geom is None:
        return False, f"Feature {feature_index}: missing geometry"

    # Only import LineString (skip Polygon pedestrian areas)
    geom_type = geom.get("type")
    if geom_type != "LineString":
        return False, f"Feature {feature_index}: skipping {geom_type} (not a road line)"

    # Must have coordinates
    coords = geom.get("coordinates")
    if not coords or len(coords) < 2:
        return False, f"Feature {feature_index}: LineString has fewer than 2 coordinates"

    # Must have a highway type
    highway = parse_highway_type(props.get("highway"))
    if not highway:
        return False, f"Feature {feature_index}: missing 'highway' property"

    # Must have an OSM ID
    osm_id = props.get("@id")
    if not osm_id:
        return False, f"Feature {feature_index}: missing '@id' property"

    return True, ""


# ── Main import function ──────────────────────────────────────────────────────

def import_roads(geojson_path: Path, dry_run: bool = False, batch_size: int = 500) -> None:
    """
    Import roads from GeoJSON into road_network table.

    Args:
        geojson_path: Path to the GeoJSON file
        dry_run:      If True, validate only — do not write to DB
        batch_size:   Number of records per database batch insert
    """
    print("=" * 60)
    print("  Vadodara Road Network Import")
    print(f"  Source: OpenStreetMap contributors (ODbL License)")
    print(f"  File:   {geojson_path}")
    print(f"  Mode:   {'DRY RUN (no DB write)' if dry_run else 'LIVE IMPORT'}")
    print("=" * 60)

    # ── Load GeoJSON ─────────────────────────────────────────────────────────
    print(f"\nLoading GeoJSON...")
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"Total features in file: {len(features):,}")

    if not features:
        print("ERROR: No features found in GeoJSON. Aborting.")
        sys.exit(1)

    # ── Connect to DB ─────────────────────────────────────────────────────────
    if not dry_run:
        db = SessionLocal()
        # Check for existing records (deduplication support)
        existing_count = db.query(RoadNetwork).count()
        print(f"Existing road_network rows: {existing_count:,}")

    # ── Process features ──────────────────────────────────────────────────────
    imported = 0
    skipped_polygon = 0
    skipped_invalid = 0
    skipped_duplicate = 0
    errors = []

    import_time = datetime.now(timezone.utc)
    batch: list[dict] = []

    print(f"\nProcessing {len(features):,} features...")

    # Track OSM IDs to detect in-file duplicates
    seen_osm_ids: set[str] = set()

    for i, feature in enumerate(features):
        if i % 5000 == 0 and i > 0:
            print(f"  ... processed {i:,}/{len(features):,} features, imported so far: {imported:,}")

        props = feature.get("properties") or {}
        geom = feature.get("geometry") or {}

        # Track polygon skips separately for clear reporting
        if geom.get("type") == "Polygon":
            skipped_polygon += 1
            continue

        # Validate
        valid, reason = validate_feature(feature, i)
        if not valid:
            skipped_invalid += 1
            if len(errors) < 20:
                errors.append(reason)
            continue

        osm_id = str(props["@id"]).strip()

        # Skip in-file duplicates
        if osm_id in seen_osm_ids:
            skipped_duplicate += 1
            continue
        seen_osm_ids.add(osm_id)

        # Build row
        coords = geom.get("coordinates", [])
        try:
            length_m = linestring_length_m(coords)
        except Exception:
            length_m = None

        row = {
            "osm_id":       osm_id,
            "highway_type": parse_highway_type(props.get("highway")),
            "road_name":    parse_road_name(props.get("name")),
            "ref":          parse_ref(props.get("ref")),
            "lanes":        parse_lanes(props.get("lanes")),
            "maxspeed":     parse_maxspeed(props.get("maxspeed")),
            "oneway":       parse_oneway(props.get("oneway")),
            "surface":      parse_surface(props.get("surface")),
            "bridge":       parse_bridge(props.get("bridge")),
            "tunnel":       parse_tunnel(props.get("tunnel")),
            "road_length_m": round(length_m, 2) if length_m else None,
            "geometry_json": geom,
            "imported_at":  import_time,
        }

        batch.append(row)
        imported += 1

        # Flush batch
        if not dry_run and len(batch) >= batch_size:
            _insert_batch(db, batch)
            batch.clear()

    # Flush remaining
    if not dry_run and batch:
        _insert_batch(db, batch)
        batch.clear()

    # ── Close DB ──────────────────────────────────────────────────────────────
    if not dry_run:
        final_count = db.query(RoadNetwork).count()
        db.close()

    # ── Report ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  IMPORT RESULTS")
    print("=" * 60)
    print(f"  Total features in file:    {len(features):,}")
    print(f"  Skipped (Polygon areas):   {skipped_polygon:,}")
    print(f"  Skipped (invalid/missing): {skipped_invalid:,}")
    print(f"  Skipped (in-file dupes):   {skipped_duplicate:,}")
    print(f"  Valid roads processed:     {imported:,}")

    if dry_run:
        print(f"\n  [DRY RUN] No records written to database.")
    else:
        print(f"  Records in road_network:   {final_count:,}")

    if errors:
        print(f"\n  First {len(errors)} validation errors:")
        for err in errors:
            print(f"    - {err}")

    print("=" * 60)
    print("\n  Attribution: Road network data © OpenStreetMap contributors")
    print("  License: Open Database License (ODbL)")
    print("  Source: https://www.openstreetmap.org/copyright")
    print("  Note: Geographic data only — no traffic volume included.")
    print("=" * 60)


def _insert_batch(db, batch: list[dict]) -> None:
    """
    Insert a batch of road rows using PostgreSQL ON CONFLICT DO NOTHING.
    Safe to re-run — duplicates (same osm_id) are silently skipped.

    geometry_json is serialized to a JSON string so psycopg2 can pass it
    as a plain text parameter (PostgreSQL will auto-cast to JSONB).
    """
    import json as _json

    # Serialize geometry_json dicts to JSON strings for psycopg2 compatibility
    serialized = []
    for row in batch:
        r = dict(row)
        r["geometry_json"] = _json.dumps(r["geometry_json"])
        serialized.append(r)

    try:
        db.execute(
            text("""
                INSERT INTO road_network
                    (osm_id, highway_type, road_name, ref, lanes, maxspeed,
                     oneway, surface, bridge, tunnel, road_length_m, geometry_json, imported_at)
                VALUES
                    (:osm_id, :highway_type, :road_name, :ref, :lanes, :maxspeed,
                     :oneway, :surface, :bridge, :tunnel, :road_length_m,
                     CAST(:geometry_json AS jsonb), :imported_at)
                ON CONFLICT (osm_id) DO NOTHING
            """),
            serialized,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"ERROR during batch insert: {exc}")
        raise



# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import Vadodara road network from OpenStreetMap GeoJSON into PostgreSQL.",
    )
    parser.add_argument(
        "--geojson",
        type=Path,
        default=None,
        help="Path to the GeoJSON file (default: searches data/ then ~/Downloads/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate features only — do not write to database",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of rows per database batch insert (default: 500)",
    )
    args = parser.parse_args()

    # Resolve GeoJSON path
    geojson_path = args.geojson
    if geojson_path is None:
        for candidate in DEFAULT_PATHS:
            if candidate.exists():
                geojson_path = candidate
                break

    if geojson_path is None or not geojson_path.exists():
        print("ERROR: Could not find vadodara_road_network.geojson.")
        print("Searched:")
        for p in DEFAULT_PATHS:
            print(f"  {p}")
        print("\nUse --geojson /path/to/file to specify the location.")
        sys.exit(1)

    import_roads(geojson_path, dry_run=args.dry_run, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
