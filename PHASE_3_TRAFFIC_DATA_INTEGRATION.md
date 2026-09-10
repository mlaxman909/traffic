# SignalAI Development Phase 3
# Traffic Dataset Integration

**Project:** SignalAI – Smart Traffic Signal Optimization Platform  
**Phase:** 3 – Traffic Dataset Integration  
**Date:** 2026-09-01  
**Author:** BCA Mini Project  

---

## Objective

Import realistic historical traffic data into the SignalAI PostgreSQL database
(`traffic_records` table), expose the data via the FastAPI backend, and
document the complete data pipeline for academic evaluation.

SignalAI is a **decision-support system**. Traffic data informs AI
recommendations, which must be reviewed and approved by a human Traffic
Operator before any action is taken.

---

## Dataset Source

| Property | Value |
|---|---|
| Type | Synthetic dataset generated to mimic Kaggle traffic datasets |
| Mimics | "Traffic Flow Dataset" / "Metro Interstate Traffic Volume" style |
| Format | CSV (comma-separated values) |
| Encoding | UTF-8 |
| File | `data/raw/kaggle_traffic_dataset.csv` |

> **Note:** A real Kaggle CSV was not available in the project workspace.
> A synthetic dataset was generated using `scripts/generate_synthetic_dataset.py`
> using realistic traffic patterns (rush-hour peaks, weather variation, weekday/weekend
> differences) seeded with `RANDOM_SEED=42` for reproducibility.

---

## Dataset Description

The dataset represents **30 days of traffic observations** across **8 junctions**,
sampled every **15 minutes**, simulating a real urban traffic monitoring system.

Patterns included:
- **Rush-hour peaks:** 07:30–10:00 and 16:30–19:30 on weekdays
- **Weekend patterns:** Gentler, later-morning peaks
- **Weather variation:** Clear, Cloudy, Light Rain, Heavy Rain, Fog, Hazy
- **Missing values:** ~0.72% vehicle counts and ~0.30% congestion values (realistic data quality)

---

## Dataset Size

| Metric | Value |
|---|---|
| File size | 1.66 MB |
| Total rows | 23,040 |
| Total columns | 10 |
| Junctions | 8 |
| Days | 30 (January 2024) |
| Interval | 15 minutes |
| Missing values | 236 cells (0.10%) |
| Exact duplicates | 0 |

---

## Dataset Fields

| Column | Type | Description |
|---|---|---|
| `timestamp` | String (datetime) | Reading timestamp: YYYY-MM-DD HH:MM:SS |
| `junction_id` | String | Junction code: J-101 to J-108 |
| `location_name` | String | Human-readable junction name |
| `vehicle_count` | Integer (nullable) | Vehicles per 15-minute interval |
| `congestion_pct` | Integer (nullable) | Congestion percentage 0–100 |
| `traffic_level` | Enum string | LOW / MODERATE / HIGH / CRITICAL |
| `weather_condition` | String | Weather category at time of reading |
| `day_of_week` | String | Monday–Sunday |
| `is_weekend` | 0/1 | Weekend indicator |
| `hour_of_day` | Integer | 0–23 |

---

## SignalAI traffic_records Structure

```sql
CREATE TABLE traffic_records (
    id                    SERIAL          PRIMARY KEY,
    junction_id           INTEGER         NOT NULL REFERENCES junctions(id) ON DELETE CASCADE,
    recorded_at           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    vehicles              INTEGER         CHECK (vehicles >= 0),
    traffic_level         traffic_level   NOT NULL DEFAULT 'LOW',
    congestion_percentage INTEGER         CHECK (congestion_percentage BETWEEN 0 AND 100),
    created_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**SQLAlchemy Model:** `backend/app/models/traffic_record.py` — `TrafficRecord`  
**Pydantic Schema:** `backend/app/schemas/traffic_record.py` — `TrafficRecordRead`

---

## Column Mapping

| CSV Column | SignalAI Field | Status | Transformation |
|---|---|---|---|
| `timestamp` | `recorded_at` | **TRANSFORMED** | Parse string → timezone-aware datetime (IST +05:30) |
| `junction_id` | `junction_id` (FK) | **TRANSFORMED** | Junction code → DB integer via lookup |
| `vehicle_count` | `vehicles` | **DIRECT** | Cast int; empty string → NULL |
| `congestion_pct` | `congestion_percentage` | **DIRECT** | Cast int; empty string → NULL |
| `traffic_level` | `traffic_level` | **DIRECT** | Uppercase match to PostgreSQL ENUM |
| `location_name` | — | **NOT USED** | Redundant — already in junctions table |
| `weather_condition` | — | **NOT USED** | Not in traffic_records schema |
| `day_of_week` | — | **NOT USED** | Derivable from recorded_at |
| `is_weekend` | — | **NOT USED** | Derivable from recorded_at |
| `hour_of_day` | — | **NOT USED** | Derivable from recorded_at |

---

## Data Cleaning

**Script:** `scripts/prepare_traffic_data.py`

### Cleaning Steps Applied

| Step | Action |
|---|---|
| Column normalization | Lowercase + strip whitespace |
| Timestamp validation | Parse `YYYY-MM-DD HH:MM:SS`, reject if invalid |
| Junction ID validation | Must be in {J-101 … J-108} |
| Traffic level validation | Must match LOW/MODERATE/HIGH/CRITICAL |
| Vehicle count validation | Integer ≥ 0; empty → NULL; negative → reject |
| Congestion validation | Integer 0–100; empty → NULL; out-of-range → reject |
| Duplicate removal | One row per (junction_id, timestamp) pair |

### Cleaning Results

| Metric | Count |
|---|---|
| Original rows | 23,040 |
| Valid / cleaned rows | 23,040 |
| Rejected rows | 0 |
| NULL vehicle_count | 166 (0.72%) |
| NULL congestion_pct | 70 (0.30%) |
| Rejection rate | 0.00% |

**Output:** `data/processed/traffic_records_cleaned.csv`  
**Report:** `data/DATA_CLEANING_REPORT.md`

---

## Data Transformation

| Transformation | Detail |
|---|---|
| Timestamp → UTC-aware | `datetime.strptime` + `.replace(tzinfo=IST)` where IST = UTC+05:30 |
| Junction code → FK integer | `SELECT id FROM junctions WHERE junction_code = 'J-101'` |
| Empty string → Python None | Stored as NULL in PostgreSQL nullable columns |
| Traffic level string → ENUM | PostgreSQL `traffic_level` ENUM enforced at INSERT |

---

## Database Import

**Script:** `scripts/import_traffic_data.py`

### Import Process

1. Load `DATABASE_URL` from `backend/.env`
2. Connect to PostgreSQL via SQLAlchemy
3. Build junction_code → junction_id lookup table
4. Load existing (junction_id, recorded_at) keys for duplicate detection
5. Stream CSV row by row
6. For each row: validate → transform → check for duplicate → batch
7. Flush batch of 500 rows via parameterized `INSERT`
8. Commit transaction per batch
9. Run post-import verification queries
10. Print final report

---

## Duplicate Handling

**Strategy:** Composite key check on `(junction_id, recorded_at)`

- Before import: all existing keys are loaded into a Python `set`
- Each incoming row is checked against this set
- New keys: added to set + queued for INSERT
- Existing keys: skipped with counter incremented
- **Re-running the import is safe:** all rows will be skipped (0 duplicates inserted)

No unique constraint was added to the schema — the check is application-level,
avoiding schema changes that could break existing data.

---

## Validation

All rows are validated before INSERT:

| Field | Validation Rule |
|---|---|
| `junction_id` | Must match a known junction code |
| `recorded_at` | Must be a valid datetime |
| `traffic_level` | Must be LOW, MODERATE, HIGH, or CRITICAL |
| `vehicles` | If present: non-negative integer |
| `congestion_percentage` | If present: 0 ≤ value ≤ 100 |

Invalid rows are **skipped and counted** — not silently discarded.

---

## Import Statistics

| Metric | Value |
|---|---|
| Pre-import count | 8 |
| CSV rows read | 23,040 |
| Rows inserted | 23,040 |
| Skipped (duplicate) | 0 |
| Skipped (invalid) | 0 |
| Failed (DB error) | 0 |
| Post-import count | **23,048** |
| Import speed | ~13,880 rows/second |
| Total time | 1.66 seconds |

---

## PostgreSQL Verification

Direct SQL query result:

```sql
SELECT COUNT(*) FROM traffic_records;
-- → 23048

SELECT MIN(recorded_at), MAX(recorded_at) FROM traffic_records;
-- → 2024-01-01 00:00:00+05:30 | 2026-08-28 12:53:28+05:30

SELECT traffic_level, COUNT(*) FROM traffic_records GROUP BY traffic_level;
-- → LOW:18931  MODERATE:3926  HIGH:188  CRITICAL:3
```

**Result: PASS** ✅

---

## FastAPI Verification

| Endpoint | Method | Description | Status |
|---|---|---|---|
| `/api/traffic-records` | GET | List (paginated, filterable) | ✅ PASS |
| `/api/traffic-records/summary` | GET | Aggregated stats per junction | ✅ PASS |
| `/api/traffic-records/{id}` | GET | Single record by ID | ✅ PASS |
| Swagger UI `/docs` | — | Interactive docs with all endpoints | ✅ PASS |

All returned data is confirmed from PostgreSQL — no mock data.

---

## Screenshots To Capture

For academic submission, capture these screenshots:

1. **Dataset profile** — open `data/DATASET_PROFILE.md` and screenshot the column table
2. **Cleaned dataset** — open `data/processed/traffic_records_cleaned.csv` in a text editor, show first 10 rows
3. **Terminal import success** — run `python3 scripts/import_traffic_data.py` and screenshot the `IMPORT COMPLETE` summary box
4. **PostgreSQL count** — run in Terminal: `psql -d signalai -c "SELECT COUNT(*) FROM traffic_records;"` — screenshot shows 23048
5. **PostgreSQL sample records** — run: `psql -d signalai -c "SELECT id, junction_id, recorded_at, vehicles, traffic_level FROM traffic_records LIMIT 10;"` — screenshot the table
6. **Swagger UI** — open http://localhost:8000/docs — screenshot showing Traffic Records section
7. **API response** — expand `GET /api/traffic-records/summary` in Swagger, click Execute — screenshot the 200 response with 8 junctions
8. **Project folder structure** — in Terminal: `find . -not -path '*/node_modules/*' -not -path '*/__pycache__/*' -not -path '*/venv/*' -maxdepth 4 | sort | head -60`

---

## Files Created

| File | Purpose |
|---|---|
| `scripts/generate_synthetic_dataset.py` | Generates the synthetic CSV dataset |
| `scripts/prepare_traffic_data.py` | Cleans and validates the raw CSV |
| `scripts/import_traffic_data.py` | Imports cleaned CSV into PostgreSQL |
| `data/raw/kaggle_traffic_dataset.csv` | Raw traffic dataset (1.66 MB, 23,040 rows) |
| `data/processed/traffic_records_cleaned.csv` | Cleaned dataset ready for import |
| `data/DATASET_PROFILE.md` | Complete dataset statistical profile |
| `data/KAGGLE_TO_SIGNALAI_MAPPING.md` | Column mapping documentation |
| `data/DATA_CLEANING_REPORT.md` | Cleaning results and rejection reasons |
| `data/IMPORT_VERIFICATION.md` | Post-import SQL verification results |
| `database/signalai_after_traffic_import.sql` | Full database backup (1.7 MB) |
| `PHASE_3_TRAFFIC_DATA_INTEGRATION.md` | This document |

---

## Files Modified

| File | Change |
|---|---|
| `backend/app/routers/traffic_records.py` | **NEW** — Traffic records API router |
| `backend/app/main.py` | Added `traffic_records` router import and registration |

---

## Known Limitations

| # | Limitation | Impact | Resolution |
|---|---|---|---|
| 1 | Dataset is synthetic (not real Kaggle data) | Academic demo only | Replace with real Kaggle CSV by placing it in `data/raw/` and re-running prepare + import scripts |
| 2 | No unique DB constraint on (junction_id, recorded_at) | Application-level duplicate check only | Acceptable for Phase 3; can add DB constraint in Phase 4 |
| 3 | Timezone treated as IST (UTC+5:30) | May differ from real-world dataset | Update IST offset in import script if needed |
| 4 | 5 CSV columns not imported (weather, day, etc.) | Not in traffic_records schema | Future enhancement: add weather column to junctions |
| 5 | No real-time traffic feed | Static historical data only | Phase 5+ feature |

---

## Future Improvements

1. Replace synthetic dataset with real Kaggle CSV
2. Add `UNIQUE(junction_id, recorded_at)` constraint to traffic_records
3. Import weather_condition into `junctions.weather_condition` from dataset
4. Connect React frontend dashboard to `/api/traffic-records/summary`
5. Add time-series chart using real traffic data
6. Build AI recommendation engine based on traffic thresholds
7. Implement pagination UI in the frontend
8. Add real-time data ingestion via WebSocket or polling
