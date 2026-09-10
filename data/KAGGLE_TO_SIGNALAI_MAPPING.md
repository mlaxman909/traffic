# Kaggle Dataset → SignalAI Column Mapping
# SignalAI – Smart Traffic Signal Optimization Platform

---

## Source: Synthetic Traffic Dataset

**File:** `data/raw/kaggle_traffic_dataset.csv`  
**Columns:** 10  
**Rows:** 23,040  

---

## Target: SignalAI `traffic_records` Table

**Schema (from `database/schema.sql`):**

| Column | Type | Nullable | Constraint |
|---|---|---|---|
| `id` | SERIAL | NOT NULL | PRIMARY KEY (auto-generated) |
| `junction_id` | INTEGER | NOT NULL | FK → junctions.id (CASCADE) |
| `recorded_at` | TIMESTAMPTZ | NOT NULL | DEFAULT NOW() |
| `vehicles` | INTEGER | NULL | CHECK vehicles >= 0 |
| `traffic_level` | traffic_level ENUM | NOT NULL | DEFAULT 'LOW' |
| `congestion_percentage` | INTEGER | NULL | CHECK 0–100 |
| `created_at` | TIMESTAMPTZ | NOT NULL | DEFAULT NOW() |

---

## Full Column Mapping Table

| Kaggle Column | Type | SignalAI Field | Table | Transformation | Status |
|---|---|---|---|---|---|
| `timestamp` | String | `recorded_at` | traffic_records | Parse `YYYY-MM-DD HH:MM:SS` → Python datetime → UTC-aware | **TRANSFORMED** |
| `junction_id` | String (J-101 etc.) | `junction_id` | traffic_records | Lookup `junctions.id` WHERE `junction_code = value` | **TRANSFORMED** |
| `vehicle_count` | Integer / empty | `vehicles` | traffic_records | Cast to int; empty string → NULL | **TRANSFORMED** |
| `congestion_pct` | Integer / empty | `congestion_percentage` | traffic_records | Cast to int; empty string → NULL; enforce 0–100 | **TRANSFORMED** |
| `traffic_level` | String enum | `traffic_level` | traffic_records | Uppercase match to TrafficLevel enum | **DIRECT** |
| `location_name` | String | — | — | Used only for junction lookup validation; not stored | **NOT USED** |
| `weather_condition` | String | — | — | Not in traffic_records model; junctions.weather_condition is updated separately | **NOT USED** |
| `day_of_week` | String | — | — | Fully derivable from `timestamp`; no separate column exists in traffic_records | **NOT USED** |
| `is_weekend` | 0/1 | — | — | Derivable from `timestamp`; no separate column exists | **NOT USED** |
| `hour_of_day` | Integer | — | — | Derivable from `timestamp`; no separate column exists | **NOT USED** |

---

## Transformation Details

### 1. `timestamp` → `recorded_at`
```
Input:  "2024-01-15 08:30:00"   (naive string)
Parse:  datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
Output: 2024-01-15T08:30:00+05:30  (timezone-aware IST)
```
- Treated as Indian Standard Time (IST, UTC+5:30) for the purpose of this demo
- Stored as `TIMESTAMPTZ` in PostgreSQL

### 2. `junction_id` → `junction_id` (FK integer)
```
Input:  "J-101"   (string junction code)
Lookup: SELECT id FROM junctions WHERE junction_code = 'J-101'
Output: 1         (integer primary key)
```
- Lookup table built once at import start
- Records with unknown junction codes are **rejected**
- All 8 codes (J-101 through J-108) are present in the signalai database

### 3. `vehicle_count` → `vehicles`
```
Input:  "127"   → 127  (int, valid)
Input:  ""      → None  (NULL, missing value — 0.72% of rows)
Input:  "-5"    → REJECTED (negative vehicle count invalid)
```

### 4. `congestion_pct` → `congestion_percentage`
```
Input:  "65"    → 65   (int, valid)
Input:  ""      → None  (NULL, 0.30% of rows)
Input:  "101"   → REJECTED (exceeds 100%)
Input:  "-1"    → REJECTED (below 0%)
```

### 5. `traffic_level` → `traffic_level` (ENUM)
```
Input:  "LOW"      → TrafficLevel.LOW      ✓
Input:  "MODERATE" → TrafficLevel.MODERATE  ✓
Input:  "HIGH"     → TrafficLevel.HIGH      ✓
Input:  "CRITICAL" → TrafficLevel.CRITICAL  ✓
Input:  "unknown"  → REJECTED (not in enum)
```

---

## Junction Mapping Strategy

The dataset uses explicit `junction_id` codes that **directly correspond** to the 8 junctions seeded in the SignalAI database:

| CSV `junction_id` | DB `junction_code` | DB `id` | `location_name` in CSV |
|---|---|---|---|
| J-101 | J-101 | 1 | Main St & 5th Ave |
| J-102 | J-102 | 2 | Broadway & 8th |
| J-103 | J-103 | 3 | Park Ave & Central |
| J-104 | J-104 | 4 | Oak St & 2nd Ave |
| J-105 | J-105 | 5 | Elm Rd & North Ring |
| J-106 | J-106 | 6 | Lake View & Sector 3 |
| J-107 | J-107 | 7 | Industrial Bypass |
| J-108 | J-108 | 8 | Station Rd & MG Ave |

**Strategy:** Direct code-to-ID lookup. No ambiguity. No invented mapping needed.

---

## Duplicate Detection Strategy

The `traffic_records` table has **no explicit unique constraint** on `(junction_id, recorded_at)`.  
To prevent re-importing the same rows if the script is run twice, we use:

**Composite key:** `(junction_id, recorded_at)`

Logic:
1. At script start, load all existing `(junction_id, recorded_at)` pairs from DB
2. For each CSV row, compute the key after transformation
3. If key already exists in DB → **SKIP** (log as duplicate)
4. If key is new → **INSERT**

This is safe, deterministic, and requires no schema change.

---

## Fields Not Mapped and Why

| Field | Reason Not Mapped |
|---|---|
| `location_name` | Redundant — junction name already in `junctions.name` |
| `weather_condition` | Not in `traffic_records` schema. `junctions.weather_condition` is a snapshot field updated separately |
| `day_of_week` | No corresponding column in `traffic_records`. Derivable: `extract(DOW FROM recorded_at)` |
| `is_weekend` | Same as above — fully derivable from `recorded_at` |
| `hour_of_day` | Same — fully derivable: `extract(HOUR FROM recorded_at)` |
