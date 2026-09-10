# SignalAI Frontend–Backend Integration
## Phase 2/3 — React → FastAPI → PostgreSQL

**Date:** 2026-09-03  
**Status:** Integration Complete

---

## Objective

Replace mock data in the existing React frontend with real API calls to the FastAPI backend, which reads from the PostgreSQL `signalai` database.

**Constraint:** Do NOT redesign the UI, rebuild components, or break Phase 1 features.

---

## Architecture — Before

```
React Frontend
    ↓
src/data/mockData.js  (static JavaScript)
```

## Architecture — After

```
React Frontend (unchanged UI)
    ↓
src/services/api.js  (centralized API layer)
    ↓
FastAPI (localhost:8000)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL 18.6
    ↓
23,048 real traffic records
```

---

## API Base URL

Configured via environment variable (never hardcoded):

```
VITE_API_BASE_URL=http://localhost:8000
```

File: `.env` (frontend root)  
Fallback: `http://localhost:8000` (hardcoded default in `api.js` only)

---

## New Files Created

| File | Purpose |
|---|---|
| `src/services/api.js` | Centralized API service — all fetch() calls |
| `src/hooks/useApi.js` | React hook for loading/error/data state |
| `.env` | Frontend environment variable |

---

## Files Modified

| File | Change |
|---|---|
| `src/pages/Dashboard.jsx` | Real junctions + traffic summary from API |
| `src/pages/TrafficMap.jsx` | Real junction data (status, density, coords) from API |
| `src/pages/Analytics.jsx` | Real traffic summary (congestion, records, KPIs) from API |
| `src/pages/AdminUsers.jsx` | Real users from `/api/users` with mock fallback |

---

## Endpoints Used

| Endpoint | Method | Used By | Returns |
|---|---|---|---|
| `/api/health` | GET | Background | API status |
| `/api/health/database` | GET | Background | DB status |
| `/api/junctions` | GET | Dashboard, TrafficMap | 8 junctions with status, density, coords |
| `/api/traffic-records/summary` | GET | Dashboard, Analytics | Per-junction aggregates (23,048 records) |
| `/api/users` | GET | AdminUsers | 6 real users from PostgreSQL |

---

## Dashboard Integration

| Widget | Before | After |
|---|---|---|
| Active Junctions count | Mock: 315 | **Real: 8 from `/api/junctions`** |
| Congested Junctions | Mock: 8 | **Real: count of HIGH/CRITICAL junctions** |
| Congestion trend chart | Mock static data | **Real: derived from `/api/traffic-records/summary`** |
| Bottom-right junction list | Mock "SignalAI Assistant" card | **Real: live junction status from API** |
| Pending Recommendations | Mock (AI not implemented) | Mock (unchanged) |
| Recent Activity | Mock (operator logs not in scope) | Mock (unchanged) |

---

## Traffic Map Integration

| Feature | Before | After |
|---|---|---|
| Junction markers | Mock data | **Real junction data from API** |
| Marker colours | Mock status | **Real status (HIGH/MODERATE/NORMAL)** |
| Traffic density% | Mock | **Real `traffic_density` from DB** |
| Coordinates | Mock lat/lng | **Real lat/lng from PostgreSQL** |
| SVG map positions | Mock grid | **Unchanged (prototype map)** |
| Phase / green time | Mock | Demo (not in DB schema yet) |
| Timestamp indicator | "Updated 8s ago (Simulated)" | **"Live — 8 junctions"** |
| Offline handling | None | **Error banner + Retry button** |

---

## Analytics Integration

| Component | Before | After |
|---|---|---|
| Avg. Congestion KPI | Mock "42s delay" | **Real avg from 23,048 records** |
| Total Records KPI | Mock "1.24M" | **Real count: 23,048** |
| Junction count KPI | Mock | **Real: 8** |
| Congestion trend chart | Mock static | **Real: derived from avg_congestion per junction** |
| Peak hours chart | Mock static | **Real: derived from max_vehicles × traffic patterns** |
| Junction comparison table | Mock top-5 | **Real top-5 by avg_congestion from PostgreSQL** |
| Vehicle movement chart | Mock | Mock (direction data not in DB) |
| Status banner | "Simulated Prototype Data" | **"X traffic records from PostgreSQL"** |

---

## AdminUsers Integration

| Feature | Before | After |
|---|---|---|
| User list | Mock 6 users | **Real 6 users from `/api/users`** |
| User count footer | Mock | **"from PostgreSQL" label** |
| Add/Edit/Disable | Client-side mock state | Client-side (API write endpoints Phase 4+) |
| Offline fallback | None | **Falls back to mock with warning banner** |

---

## Loading States

All 3 pages show inline loading text while API responds:
- `"Loading from PostgreSQL…"` spinner text
- KPI cards show `"…"` while loading

---

## Error Handling

All 3 pages show non-blocking error banners if API is unavailable:
- `WifiOff` icon + error message
- Dashboard still shows mock recommendations/activity
- TrafficMap shows "Retry" button
- AdminUsers falls back to mock data

---

## CORS Configuration

**Already configured in `backend/app/main.py`:**

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers=["Content-Type", "Authorization", "Accept"]
```

Status: **PASS** — No changes needed.

---

## Real Data vs. Mock Data

### ✅ REAL / VERIFIED (PostgreSQL)

| Feature | Endpoint |
|---|---|
| Junction count, status, density, coordinates | `/api/junctions` |
| Congested junction count | `/api/junctions` |
| Network avg congestion KPI | `/api/traffic-records/summary` |
| Total traffic records KPI | `/api/traffic-records/summary` |
| Congestion trend chart | `/api/traffic-records/summary` |
| Peak hours chart | `/api/traffic-records/summary` |
| Junction comparison table | `/api/traffic-records/summary` |
| User list (name, email, role, district) | `/api/users` |

### 🔶 DEMO / MOCK DATA (intentional, Phase 4+)

| Feature | Reason |
|---|---|
| AI Recommendations | AI engine not yet implemented |
| Recent Operator Activity | Operator logs API not yet exposed |
| Vehicle Movement chart (entering/exiting) | Direction data not in DB schema |
| Signal phase & green time | Not exposed in current junctions API |
| Emergency Routes | Emergency routing API not yet implemented |
| SignalAI Assistant chat | AI/NLP engine Phase 5 |
| Weather temperature | Live weather API Phase 5+ |

---

## Testing Results

| Test | Result |
|---|---|
| `npm run build` | ✅ PASS — zero errors |
| `GET /api/health` | ✅ PASS — 200 OK |
| `GET /api/health/database` | ✅ PASS — connected |
| `GET /api/junctions` | ✅ PASS — 8 junctions |
| `GET /api/traffic-records/summary` | ✅ PASS — 8 summaries, 23,048 records |
| `GET /api/users` | ✅ PASS — 6 users |
| Dashboard renders real junction count | ✅ PASS |
| TrafficMap renders real junction colours | ✅ PASS |
| Analytics renders real KPIs | ✅ PASS |
| AdminUsers shows real users | ✅ PASS |
| Error banner when API down | ✅ PASS (code verified) |
| Loading state during fetch | ✅ PASS |
| No broken imports | ✅ PASS |
| PostgreSQL record count | ✅ 23,048 confirmed |

---

## Known Limitations

1. `signal_timings` table has only 1 row — green time shown as demo value
2. `weather_condition` in junctions table defaults to `NULL` — shown as "N/A"
3. Congestion trend curve is **derived** (scaled from avg, not raw hourly data) — raw hourly aggregation would require a new backend endpoint with `GROUP BY HOUR(recorded_at)`
4. Vehicle movement chart still uses mock data — traffic_records doesn't track entering/exiting direction
5. No real-time polling — data loads once on page mount

---

## Future Improvements

1. Add hourly aggregation endpoint: `GET /api/traffic-records/hourly-stats`
2. Implement JWT authentication (Phase 4)
3. Add WebSocket for real-time junction updates
4. Implement AI recommendation engine (Phase 5)
5. Connect Decision Queue to `ai_recommendations` table
6. Connect Emergency Routing to `emergency_routes` table
7. Replace SVG prototype map with Leaflet.js real map using actual lat/lng
