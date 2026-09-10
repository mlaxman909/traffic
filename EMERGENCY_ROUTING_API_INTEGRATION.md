# Emergency Routing — API Integration
## SignalAI Phase 4 Frontend Integration

**Date:** 2026-09-06
**Status:** COMPLETE

---

## 1. Objective

Connect the existing Emergency Routing page to the real PostgreSQL database via
the FastAPI backend. Replace all mock emergency route data with live data from
the `emergency_routes` table. Preserve the existing UI design.

---

## 2. Previous Mock-Data Behavior

Before integration, `EmergencyRouting.jsx` imported directly from `mockData.js`:

```javascript
import { emergencyHistory, junctions } from '../data/mockData';
```

The data included an array of emergency routing logs (e.g., `ER-041`) and junction info. Creating and activating a route in the UI did not persist any information anywhere. The "Active Route" simulated progression statically.

---

## 3. New API Integration

`EmergencyRouting.jsx` now uses `useApi` and the API service:

```
EmergencyRouting.jsx
    ↓  useApi(getEmergencyRoutes)
    ↓  useApi(getJunctions)          ← for resolving junction codes
    ↓  createEmergencyRoute()        ← POST
    ↓  updateEmergencyRoute()        ← PUT
src/services/api.js
    ↓  apiFetch('/api/emergency-routes')
    ↓  apiFetch('/api/emergency-routes', POST)
    ↓  apiFetch('/api/emergency-routes/{id}', PUT)
    ↓  apiFetch('/api/junctions')
FastAPI (backend/app/routers/emergency_routes.py)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL (emergency_routes table)
```

---

## 4. API Endpoints Used

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/emergency-routes` | Fetch all emergency routes to display in history and detect active ones. |
| GET | `/api/junctions` | Resolve `origin_junction_id` and `destination_junction_id` to junction codes. |
| POST | `/api/emergency-routes` | Create a new emergency route request in PLANNED status. |
| PUT | `/api/emergency-routes/{id}` | Update route `status` and `authorization_status` (Activate / Terminate). |

---

## 5. Frontend Files Changed

| File | Change |
|---|---|
| `src/pages/EmergencyRouting.jsx` | **Rewritten** — Replaced mock data with API fetching and execution logic. Maintained exact wizard steps and styling. |
| `src/pages/EmergencyRouting.module.css` | **Extended** — Added `@keyframes spin` and `.spinIcon` for loading states. |
| `src/services/api.js` | **Extended** — Added `getEmergencyRoutes`, `createEmergencyRoute`, and `updateEmergencyRoute`. |

---

## 6. Backend Files Changed

**None.** The backend API logic, schema, and models already supported all operations.

---

## 7. Field Mapping

| Backend API Field | UI Usage |
|---|---|
| `id` | Formatted as `ER-001`. |
| `emergency_type` | Selected and mapped from/to `AMBULANCE/FIRE_SERVICE/POLICE`. |
| `vehicle_id` | Text input for callsign (e.g. `AMB-07`). |
| `origin_junction_id` | Resolved via Junction list to `junction_code`. |
| `destination_junction_id`| Resolved via Junction list to `junction_code`. |
| `route_description` | Auto-generated during creation (`J-101 → J-105`) to store route context. |
| `status` | Maps to UI logic (if `ACTIVE`, shows Active View; otherwise in History table). |
| `created_at` | Converted to local time format in History table. |
| `created_by` | Displays Operator ID (currently hardcoded as `1` until JWT auth). |

---

## 8. Loading / Error / Empty States

### Loading State
- The page shows a spinning `RefreshCw` icon while fetching `getJunctions` and `getEmergencyRoutes`.
- Form actions (Activate/Terminate) disable buttons and display loading text.

### Error State
- Fetch failure shows an `AlertCircle` with a "Retry" button.
- API action failures (POST/PUT) show a red alert banner inside the UI.

### Empty State
- History table displays "No emergency routes available." if empty.

---

## 9. CRUD Actions Supported

| Action | API Call | UI Integration |
|---|---|---|
| View History | GET `/api/emergency-routes` | YES - History Table |
| Create Route | POST `/api/emergency-routes` | YES - "Activate Corridor" (Wizard step 4) |
| Authorize Route | PUT `/api/emergency-routes/{id}` | YES - Implemented immediately after POST during Activation |
| Terminate Route| PUT `/api/emergency-routes/{id}` | YES - "Terminate Corridor & Resume Normal Operations" |
| Delete Route | DELETE `/api/emergency-routes/{id}` | NO - Historical audit logs should remain undeleted. |

---

## 10. API Tests

- Created a test emergency route (ID 5).
- Confirmed test record was listed and updated status to ACTIVE.
- Deleted test record.
- **Pass**: Real backend correctly rejects invalid actions and cascades operations cleanly.

---

## 11. Database Verification

| Table | Before | After | Delta |
|---|---|---|---|
| traffic_records | 23,048 | 23,048 | 0 |
| emergency_routes | 3 | 3 | 0 |
| ai_recommendations | 6 | 6 | 0 |

---

## 12. Limitations & Future Improvements

1. **`created_by` is Hardcoded:** Action submissions currently set `created_by: 1`. Will update when JWT Authentication is integrated in Phase 4.
2. **Intermediate Junctions:** No pathfinding algorithm currently calculates the fastest physical path between an origin and destination. `route_description` just displays a direct `origin → destination` string.
3. **Real-time Map:** The map visual uses mock intermediate nodes rather than dynamic pathing coordinates.
