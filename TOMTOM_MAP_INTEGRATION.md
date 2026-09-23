# SignalAI — TomTom Map Integration
## Phase 4 Documentation

**Date:** 22 September 2026  

---

## Map Provider

**TomTom Maps API** — Raster tile service

- API version: v1 (confirmed working with HTTP 200)
- Tile URL: `https://api.tomtom.com/map/1/tile/basic/main/{z}/{x}/{y}.png`
- Renderer: MapLibre GL JS (loaded via CDN — no bundler dependency)
- API key: `VITE_TOMTOM_API_KEY` environment variable in `.env`

---

## Architecture

```
Browser
  └─ index.html
       └─ <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js">
  └─ TrafficMap.jsx
       └─ window.maplibregl  (CDN global)
            └─ new Map({ style: getTomTomStyle(VITE_TOMTOM_API_KEY) })
                  └─ TomTom raster tiles
```

**Why CDN instead of npm import?**  
MapLibre GL v6 uses WebWorkers which cause Vite bundler conflicts. Loading via CDN `<script>` tag eliminates all bundler/import issues and is the officially recommended approach for browser-only usage.

---

## Environment Variable

```env
# .env
VITE_TOMTOM_API_KEY=<your-key-here>
```

> ⚠️ The API key is **never hardcoded** in source code. It is accessed via `import.meta.env.VITE_TOMTOM_API_KEY` in the React component.

---

## Map Features Implemented

| Feature | Status |
|---------|--------|
| Raster tile map (TomTom basemap) | ✅ Working |
| Map centred on Vadodara (22.3076°N, 73.1866°E) | ✅ |
| Zoom level 13 (street level) | ✅ |
| Navigation controls (zoom +/-) | ✅ |
| Attribution control | ✅ |
| 8 Junction markers (real coordinates from DB) | ✅ |
| Marker anchor: center (precise GPS placement) | ✅ |
| Color coding by traffic status | ✅ |
| Hover popup with junction name | ✅ |
| Click to open detail panel | ✅ |
| Search filter | ✅ |
| Status filter (All/Congested/Moderate/Low) | ✅ |
| Legend | ✅ |

---

## Data Sources (Clearly Separated)

| Data | Source |
|------|--------|
| Map tiles / basemap | TomTom Maps API |
| Junction locations (lat/lng) | SignalAI PostgreSQL database |
| Traffic density / status | SignalAI PostgreSQL database |
| Road network overlay | OpenStreetMap (45,903 road records) |

> TomTom provides the **visual basemap only**. All SignalAI traffic data is owned by and retrieved from the SignalAI PostgreSQL database.

---

## API Key Verification

Verified 22 Sept 2026:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "https://api.tomtom.com/map/1/tile/basic/main/13/6280/3849.png?key=<KEY>"
# Result: 200
```

---

## Junction Coordinates (Vadodara)

| Code | Name | Latitude | Longitude |
|------|------|----------|-----------|
| J-101 | Genda Circle | 22.3056 | 73.1764 |
| J-102 | Kala Ghoda Circle | 22.3054 | 73.1818 |
| J-103 | Chakli Circle | 22.3086 | 73.1650 |
| J-104 | Fatehgunj Circle | 22.3207 | 73.1882 |
| J-105 | Amit Nagar Circle | 22.3168 | 73.1975 |
| J-106 | Susen Circle | 22.2994 | 73.2081 |
| J-107 | Muktanand Circle | 22.3218 | 73.1979 |
| J-108 | Akota Circle | 22.2933 | 73.1721 |
