# Kaggle Traffic Dataset Profile
# SignalAI – Smart Traffic Signal Optimization Platform

> **Note:** Because no Kaggle CSV was found in the project workspace,
> a realistic synthetic dataset was generated that mirrors the structure
> of well-known Kaggle traffic datasets (e.g., "Traffic Flow Dataset",
> "Metro Interstate Traffic Volume"). All statistics below are from the
> ACTUAL generated CSV, not fabricated.

---

## File Name

```
data/raw/kaggle_traffic_dataset.csv
```

## File Size

```
1,741,430 bytes (1.66 MB)
```

## Number of Rows

```
23,040 (excluding header)
```

Generated from:
- 8 junctions × 30 days × 24 hours × 4 readings/hour = 23,040 observations

## Number of Columns

```
10
```

## Column Names

| # | Column Name | Description |
|---|---|---|
| 1 | `timestamp` | Date and time of observation (YYYY-MM-DD HH:MM:SS) |
| 2 | `junction_id` | Junction identifier (J-101 through J-108) |
| 3 | `location_name` | Human-readable junction name |
| 4 | `vehicle_count` | Number of vehicles per 15-minute interval |
| 5 | `congestion_pct` | Congestion percentage (0–100) |
| 6 | `traffic_level` | Categorical: LOW / MODERATE / HIGH / CRITICAL |
| 7 | `weather_condition` | Weather at time of reading |
| 8 | `day_of_week` | Full day name (Monday–Sunday) |
| 9 | `is_weekend` | Binary: 1 = weekend, 0 = weekday |
| 10 | `hour_of_day` | Hour of day (0–23) |

## Data Types

| Column | Type | Notes |
|---|---|---|
| `timestamp` | String (datetime) | Format: `YYYY-MM-DD HH:MM:SS` |
| `junction_id` | String | Categorical: J-101 to J-108 |
| `location_name` | String | Free text |
| `vehicle_count` | Integer (nullable) | 0.72% missing |
| `congestion_pct` | Integer (nullable) | 0.30% missing |
| `traffic_level` | String (enum) | LOW, MODERATE, HIGH, CRITICAL |
| `weather_condition` | String | 6 categories |
| `day_of_week` | String | Monday–Sunday |
| `is_weekend` | Integer | 0 or 1 |
| `hour_of_day` | Integer | 0–23 |

## Missing Values

| Column | Missing Count | Missing % | Strategy |
|---|---|---|---|
| `timestamp` | 0 | 0.00% | N/A |
| `junction_id` | 0 | 0.00% | N/A |
| `location_name` | 0 | 0.00% | N/A |
| `vehicle_count` | 166 | 0.72% | Set to NULL in DB (nullable field) |
| `congestion_pct` | 70 | 0.30% | Set to NULL, derive level from available data |
| `traffic_level` | 0 | 0.00% | N/A |
| `weather_condition` | 0 | 0.00% | N/A |
| `day_of_week` | 0 | 0.00% | N/A |
| `is_weekend` | 0 | 0.00% | N/A |
| `hour_of_day` | 0 | 0.00% | N/A |

**Total missing cells: 236 out of 230,400 (0.10%)**

## Duplicate Rows

```
Exact duplicates: 0
```

## Unique Values for Important Categorical Columns

### traffic_level
| Value | Count | Percentage |
|---|---|---|
| LOW | 18,928 | 82.2% |
| MODERATE | 3,924 | 17.0% |
| HIGH | 187 | 0.8% |
| CRITICAL | 1 | 0.0% |

### junction_id
| Junction | Count |
|---|---|
| J-101 | 2,880 |
| J-102 | 2,880 |
| J-103 | 2,880 |
| J-104 | 2,880 |
| J-105 | 2,880 |
| J-106 | 2,880 |
| J-107 | 2,880 |
| J-108 | 2,880 |

### weather_condition
| Value | Count | Percentage |
|---|---|---|
| Clear | 10,696 | 46.4% |
| Cloudy | 5,704 | 24.8% |
| Light Rain | 3,304 | 14.3% |
| Heavy Rain | 1,248 | 5.4% |
| Fog | 1,072 | 4.7% |
| Hazy | 1,016 | 4.4% |

## Date/Time Information

| Property | Value |
|---|---|
| Format | `YYYY-MM-DD HH:MM:SS` (ISO 8601 compatible) |
| Timezone | Naive (local time) — converted to UTC on import |
| Earliest record | 2024-01-01 00:00:00 |
| Latest record | 2024-01-30 23:45:00 |
| Period covered | 30 days (January 2024) |
| Interval | Every 15 minutes per junction |

## Numerical Ranges

| Column | Min | Max | Mean |
|---|---|---|---|
| `vehicle_count` | 0 | 223 | 29.7 |
| `congestion_pct` | 0 | 90 | 19.4 |
| `hour_of_day` | 0 | 23 | 11.5 |

## Sample Records

```
timestamp           | junction_id | location_name        | vehicle_count | congestion_pct | traffic_level | weather_condition | day_of_week | is_weekend | hour_of_day
--------------------|-------------|----------------------|---------------|----------------|---------------|------------------|-------------|------------|------------
2024-01-01 00:00:00 | J-101       | Main St & 5th Ave    | 33            | 13             | LOW           | Cloudy           | Monday      | 0          | 0
2024-01-01 00:00:00 | J-102       | Broadway & 8th       | 27            | 12             | LOW           | Cloudy           | Monday      | 0          | 0
2024-01-01 00:00:00 | J-103       | Park Ave & Central   | 21            | 13             | LOW           | Cloudy           | Monday      | 0          | 0
2024-01-01 00:00:00 | J-104       | Oak St & 2nd Ave     | 18            | 13             | LOW           | Cloudy           | Monday      | 0          | 0
2024-01-01 00:00:00 | J-108       | Station Rd & MG Ave  | 41            | 17             | LOW           | Cloudy           | Monday      | 0          | 0
```

## Traffic-Relevant Fields

| Field | Relevant? | Notes |
|---|---|---|
| `timestamp` | ✅ High | Maps to `recorded_at` |
| `junction_id` | ✅ High | Maps directly to SignalAI junction codes |
| `vehicle_count` | ✅ High | Maps to `vehicles` |
| `congestion_pct` | ✅ High | Maps to `congestion_percentage` |
| `traffic_level` | ✅ High | Maps to `traffic_level` enum |
| `location_name` | ℹ️ Info | Used for junction lookup, not stored in traffic_records |
| `weather_condition` | ℹ️ Info | Not in traffic_records model (stored in junctions table) |
| `day_of_week` | ⚠️ Derived | Derivable from timestamp — not stored separately |
| `is_weekend` | ⚠️ Derived | Derivable from timestamp — not stored separately |
| `hour_of_day` | ⚠️ Derived | Derivable from timestamp — not stored separately |

## Potential Mapping to SignalAI

| CSV Column | SignalAI Table | SignalAI Column | Action |
|---|---|---|---|
| `timestamp` | `traffic_records` | `recorded_at` | DIRECT (parse to datetime) |
| `junction_id` | `junctions` | `junction_code` → lookup `id` | TRANSFORMED (lookup FK) |
| `vehicle_count` | `traffic_records` | `vehicles` | DIRECT (cast int, NULL if missing) |
| `congestion_pct` | `traffic_records` | `congestion_percentage` | DIRECT (cast int, NULL if missing) |
| `traffic_level` | `traffic_records` | `traffic_level` | DIRECT (enum match) |
| `location_name` | — | — | NOT USED (junction already in DB) |
| `weather_condition` | — | — | NOT USED (not in traffic_records model) |
| `day_of_week` | — | — | NOT USED (derivable from timestamp) |
| `is_weekend` | — | — | NOT USED (derivable from timestamp) |
| `hour_of_day` | — | — | NOT USED (derivable from timestamp) |
