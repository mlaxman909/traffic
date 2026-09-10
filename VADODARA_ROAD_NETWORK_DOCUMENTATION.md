# Vadodara Road Network Documentation

**Project:** SignalAI — Smart Traffic Signal Optimization Platform  
**Date:** 2026-09-09  
**Author:** Integration Engineer

---

## 1. Dataset Source

| Property | Value |
|---|---|
| **Source** | OpenStreetMap contributors |
| **License** | Open Database License (ODbL) |
| **Attribution URL** | https://www.openstreetmap.org/copyright |
| **Coverage** | Vadodara (Baroda), Gujarat, India |
| **Dataset type** | Static road network — geographic data only |
| **Does NOT include** | Traffic volume, vehicle counts, congestion, real-time data |

> [!IMPORTANT]
> OpenStreetMap provides **geographic road network data ONLY**.  
> It does NOT provide live traffic data, vehicle counts, or congestion levels.  
> Traffic data in SignalAI comes from the existing `traffic_records` table (23,048 records).

---

## 2. Download Method

The file was downloaded from the OpenStreetMap Overpass API or an OSM data export service.

**File name:** `vadodara_road_network.geojson`  
**Project path:** `data/vadodara_road_network.geojson`  
**File size:** ~35 MB  
**Format:** GeoJSON FeatureCollection (RFC 7946)

---

## 3. Dataset Structure

```
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[lon, lat], ...]
      },
      "properties": {
        "@id": "way/28812561",
        "highway": "primary",
        "name": "NH48",
        "oneway": "yes",
        ...
      }
    },
    ...
  ]
}
```

**Total features:** 45,909  
**LineString (road segments):** 45,903 — imported  
**Polygon (pedestrian areas):** 6 — skipped (not road centerlines)

---

## 4. Database Schema

### Table: `road_network`

```sql
CREATE TABLE road_network (
    id            SERIAL PRIMARY KEY,
    osm_id        VARCHAR(30) NOT NULL UNIQUE,  -- e.g. "way/28812561"
    highway_type  VARCHAR(50) NOT NULL,          -- OSM highway tag
    road_name     VARCHAR(300),                  -- OSM name (2% of roads)
    ref           VARCHAR(50),                   -- Road ref (NH48, SH87 etc.)
    lanes         INTEGER,                       -- Number of lanes
    maxspeed      INTEGER,                       -- Speed limit in km/h
    oneway        BOOLEAN NOT NULL DEFAULT FALSE,
    surface       VARCHAR(50),                   -- asphalt, unpaved, etc.
    bridge        BOOLEAN NOT NULL DEFAULT FALSE,
    tunnel        BOOLEAN NOT NULL DEFAULT FALSE,
    road_length_m FLOAT,                         -- haversine length in metres
    geometry_json JSONB NOT NULL,                -- GeoJSON geometry object
    imported_at   TIMESTAMP WITH TIMEZONE NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX ix_road_network_osm_id       ON road_network (osm_id);
CREATE INDEX        ix_road_network_highway_type  ON road_network (highway_type);
CREATE INDEX        ix_road_network_road_name     ON road_network (road_name);
CREATE INDEX        ix_road_network_id            ON road_network (id);
```

### Why JSONB for geometry?

PostGIS is not installed in this environment. The geometry is stored as a standard PostgreSQL JSONB column containing the GeoJSON geometry object (type + coordinates array). This allows:
- Full geometry retrieval for map rendering
- GeoJSON Feature output from the API
- Safe storage without PostGIS dependency
- Reversible migration

---

## 5. Import Process

### Import Script

```
backend/import_vadodara_roads.py
```

### How to import

```bash
cd backend
source venv/bin/activate

# Dry run (validate only, no DB write):
python import_vadodara_roads.py --dry-run

# Live import:
python import_vadodara_roads.py

# Custom path:
python import_vadodara_roads.py --geojson /path/to/vadodara_road_network.geojson
```

### Import results

| Metric | Value |
|---|---|
| Total features in file | 45,909 |
| Skipped (Polygon areas) | 6 |
| Skipped (invalid/missing) | 0 |
| Skipped (in-file duplicates) | 0 |
| **Roads imported** | **45,903** |
| Deduplication | ON CONFLICT DO NOTHING (safe to re-run) |

### Alembic Migration

```
backend/alembic/versions/435764591cc0_add_road_network_table.py
```

Applied with:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

Reversible:
```bash
alembic downgrade -1  # drops road_network table only
```

---

## 6. API Endpoints

Base URL: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
Tag: **Road Network (OpenStreetMap)**

### GET /api/road-network/stats
Returns dataset statistics.

```json
{
  "total_roads": 45903,
  "roads_with_names": 898,
  "one_way_roads": 2698,
  "bridges": 1088,
  "tunnels": 95,
  "highway_breakdown": { "residential": 30752, ... },
  "data_source": "OpenStreetMap contributors (ODbL License)"
}
```

### GET /api/road-network/geojson
Returns GeoJSON FeatureCollection for map rendering.

Query parameters:
- `highway_type` — e.g. `primary`, `secondary`, `trunk`, `motorway`
- `limit` — 1–2000 (default 500)
- `skip` — offset
- `oneway` — true/false
- `has_name` — true/false

```json
{
  "type": "FeatureCollection",
  "total": 752,
  "attribution": "Road network data © OpenStreetMap contributors (ODbL)...",
  "features": [
    {
      "type": "Feature",
      "id": 3,
      "geometry": { "type": "LineString", "coordinates": [...] },
      "properties": {
        "id": 3,
        "osm_id": "way/28813567",
        "highway_type": "primary",
        "road_name": null,
        "ref": "SH158",
        "lanes": null,
        "maxspeed": null,
        "oneway": true,
        ...
      }
    }
  ]
}
```

### GET /api/road-network
Returns paginated list of roads WITHOUT geometry (for tables/lists).

### GET /api/road-network/{id}
Returns a single road with full geometry.

Returns **404** if ID not found.

---

## 7. Frontend Integration

### Files modified

| File | Change |
|---|---|
| `src/services/api.js` | Added `getRoadNetworkGeoJSON()`, `getRoadNetwork()`, `getRoadById()`, `getRoadNetworkStats()` |
| `src/pages/TrafficMap.jsx` | Added OSM road network SVG layer |

### How the road layer works

1. On page load, `TrafficMap.jsx` fetches GeoJSON from `/api/road-network/geojson` (default limit 2000)
2. Features are filtered client-side to major road types (motorway, trunk, primary, secondary, tertiary)
3. Each `LineString` is projected from WGS84 lat/lon → SVG 0–100 coordinate space using Vadodara's bounding box
4. Roads are rendered as SVG `<polyline>` elements with coordinates sampled every 4th point for performance
5. Road colors indicate **road classification** (orange=motorway, amber=primary, grey=secondary/tertiary)
6. Junction markers (red/yellow/green) are rendered **on top** of roads — fully intact

### What was NOT changed

- Junction data fetch (`getJunctions`)
- Junction marker colors (traffic status)
- Junction detail panel
- Search and filter controls
- Signal status section
- AI recommendation section
- All other pages (Dashboard, Analytics, Decision Queue, Emergency Routing, Admin, Settings)

### Loading and error states

- Road data loading: shown in the control panel next to OSM toggle
- Road API error: shown as "Road data unavailable" — does NOT affect junction functionality
- Toggle: Checkbox to show/hide the road layer
- If road API is down: junctions continue working normally

---

## 8. OpenStreetMap Attribution

The ODbL license requires that the data source be attributed wherever road data is displayed.

Attribution is present in:
1. **Map UI** — "Road data © OpenStreetMap contributors" attribution badge (bottom-right of map)
2. **API response** — `attribution` field in every GeoJSON FeatureCollection response
3. **Swagger docs** — every road-network endpoint description mentions OSM
4. **Import script** — attribution printed at end of every import
5. **This documentation**

---

## 9. Limitations

### 1. No PostGIS
Geometry stored as JSONB. Spatial queries (bounding-box filter, ST_Intersects, ST_Within, nearest-road lookup) are not available without PostGIS. Bounding-box filtering would need to be done in Python by iterating geometry coordinates.

**Impact:** Minor — the API supports highway_type filtering which is sufficient for the frontend use case.

### 2. No Road-to-Traffic Linkage
OSM road segments cannot be reliably linked to `traffic_records`. Traffic records are junction-based (linked to `junctions.id`), while OSM roads have no concept of junctions. A proper linkage would require:
- Matching junction GPS coordinates to the nearest OSM node
- Checking if the OSM way passes through that coordinate
- This is a complex GIS operation requiring PostGIS

**Decision:** These data sources are kept deliberately separate. Road lines show geography; junction markers show traffic status.

### 3. Sparse OSM Attributes
Only ~2% of roads have names, ~0.7% have lane counts, ~0.6% have speed limits. Most roads contain only the OSM ID and highway type.

### 4. Coordinate Projection
The existing SVG map uses a 0–100 prototype coordinate space. Roads are projected from WGS84 using a linear transform based on Vadodara's bounding box. This is a close approximation (sufficient for overview maps) but is not GIS-accurate.

### 5. Performance
45,903 roads are too many to render all at once in an SVG. The frontend fetches up to 2000 roads and filters to major types (~1,600 features). If needed, users can toggle the road layer off.

---

## 10. How to Re-Import

If the dataset needs to be re-imported (e.g., updated GeoJSON file):

```bash
# The import uses ON CONFLICT DO NOTHING — safe to re-run.
# Existing rows with the same osm_id will be silently skipped.
cd backend
source venv/bin/activate
python import_vadodara_roads.py

# To fully re-import fresh data, first clear the table:
# psql -U sahilp4514 -d signalai -c "TRUNCATE road_network RESTART IDENTITY;"
# Then re-run the import script.
```

> [!WARNING]
> Only truncate `road_network`. Never truncate `traffic_records`, `users`, `junctions`, or other tables.
