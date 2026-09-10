# Data Cleaning Report
## SignalAI – Traffic Dataset Preparation

**Script:** `scripts/prepare_traffic_data.py`  
**Input:**  `data/raw/kaggle_traffic_dataset.csv`  
**Output:** `data/processed/traffic_records_cleaned.csv`  
**Run Date:** 2026-09-01 22:43:53

---

## Summary

| Metric | Count |
|---|---|
| Original rows (excl. header) | 23,040 |
| Rows passed cleaning | 23,040 |
| Rows rejected (total) | 0 |
| Rejection rate | 0.00% |
| Valid NULL vehicle_count | 166 |
| Valid NULL congestion_pct | 70 |
| Duplicate (junction,timestamp) pairs removed | 0 |

---

## Rejection Breakdown

| Rejection Reason | Count |
|---|---|

---

## Transformations Applied

| Step | Action |
|---|---|
| Column normalization | All column names lowercased and stripped |
| Timestamp parsing | Parsed from `YYYY-MM-DD HH:MM:SS` format |
| junction_id normalization | Uppercased before lookup |
| traffic_level normalization | Uppercased for enum match |
| vehicle_count empty → NULL | Stored as empty string in CSV → NULL in DB |
| congestion_pct empty → NULL | Stored as empty string in CSV → NULL in DB |
| Duplicate removal | One row kept per (junction_id, timestamp) pair |

---

## Validation Rules Applied

| Field | Rule | Action on Violation |
|---|---|---|
| `timestamp` | Must be non-empty and match `YYYY-MM-DD HH:MM:SS` | REJECT row |
| `junction_id` | Must be non-empty and in known set (J-101 to J-108) | REJECT row |
| `traffic_level` | Must match LOW/MODERATE/HIGH/CRITICAL | REJECT row |
| `vehicle_count` | If present, must be integer >= 0 | REJECT if negative |
| `congestion_pct` | If present, must be integer 0–100 | REJECT if out of range |
| `(junction_id, timestamp)` | Must be unique | REJECT duplicate |

---

## Columns Removed in Cleaned Output

The following columns from the raw CSV were dropped (not needed in DB):

| Column | Reason |
|---|---|
| `location_name` | Redundant — already in `junctions.name` |
| `weather_condition` | Not in `traffic_records` schema |
| `day_of_week` | Derivable from timestamp |
| `is_weekend` | Derivable from timestamp |
| `hour_of_day` | Derivable from timestamp |

---

## Cleaned Output Columns

| Column | Maps to DB Field |
|---|---|
| `timestamp` | `recorded_at` |
| `junction_id` | lookup → `junction_id` (FK integer) |
| `vehicle_count` | `vehicles` |
| `congestion_pct` | `congestion_percentage` |
| `traffic_level` | `traffic_level` |
