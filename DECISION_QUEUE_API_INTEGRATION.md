# Decision Queue — API Integration
## SignalAI Phase 3 Frontend Integration

**Date:** 2026-09-06
**Status:** COMPLETE

---

## 1. Objective

Connect the existing Decision Queue page to the real PostgreSQL database via
the FastAPI backend. Replace all mock recommendation data with live data from
the `ai_recommendations` table. Preserve the existing UI design exactly.

---

## 2. Previous Mock-Data Behaviour

Before this integration, `DecisionQueue.jsx` imported directly from `mockData.js`:

```js
// OLD (removed)
import { recommendations } from '../data/mockData';
const [queue, setQueue] = useState(recommendations);
```

The mock array had 6 hardcoded recommendations with fake IDs like `AI-9042`,
fake congestion percentages, fake vehicle counts, and fake expectedImpact text.
Approve/reject only mutated local React state — nothing was ever written to
the database.

---

## 3. New API Integration

`DecisionQueue.jsx` now uses the existing `useApi` hook and three methods
from `src/services/api.js`:

```
DecisionQueue.jsx
    ↓  useApi(getAiRecommendations)
    ↓  useApi(getJunctions)          ← for junction name lookup
    ↓  updateAiRecommendation(id, payload)   ← approve / reject
src/services/api.js
    ↓  apiFetch('/api/ai-recommendations')
    ↓  apiFetch('/api/junctions')
    ↓  apiFetch('/api/ai-recommendations/{id}', PUT)
FastAPI  (backend/app/routers/ai_recommendations.py)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL  (ai_recommendations table)
```

---

## 4. API Endpoints Used

| Method | URL | Purpose |
|---|---|---|
| GET | /api/ai-recommendations | Fetch all recommendations (with optional status/severity/junction_id filters) |
| GET | /api/junctions | Fetch all junctions for ID → name resolution |
| PUT | /api/ai-recommendations/{id} | Approve or Reject a PENDING recommendation |

No new backend endpoints were created. All endpoints were implemented in Phase 3.

---

## 5. Frontend Files Changed

| File | Change |
|---|---|
| `src/pages/DecisionQueue.jsx` | **Rewritten** — uses real API instead of mockData |
| `src/pages/DecisionQueue.module.css` | **Extended** — added `@keyframes spin` + `.spinIcon` for loading spinner |
| `src/services/api.js` | **Extended** — added `getAiRecommendations`, `getAiRecommendation`, `updateAiRecommendation` |

---

## 6. Backend Files Changed

**None.** The Phase 3 backend implementation was complete and required no modifications.

---

## 7. Field Mapping

The API returns snake_case fields. These are mapped to the UI as follows:

| API field | UI usage | Notes |
|---|---|---|
| `id` (integer) | Displayed as `REC-001` | Padded with `String(id).padStart(3,'0')` |
| `junction_id` | Looked up in junctions list → `junction_code`, `name` | Fetched from `/api/junctions` |
| `recommendation_text` | "Suggested Action" in detail pane | Main action text |
| `reason` | "Analysis" in AI section | Reason provided for the recommendation |
| `severity` (`CRITICAL/HIGH/MEDIUM/LOW`) | Badge color: red/red/yellow/green | Uppercased enum from DB |
| `status` (`PENDING/APPROVED/REJECTED`) | Tab routing | Lowercased for tab comparison |
| `current_green_time` | Current green time display in seconds | `—` if null |
| `suggested_green_time` | Suggested green time display | `—` if null |
| `created_at` (ISO 8601) | Formatted to `12:45 PM` in list, `28 Aug 2026, 12:45 PM` in detail | |
| `reviewed_at` | Shown in approved/rejected review section | |
| `rejection_reason` | Shown in rejected detail view | |

Fields **not in the API** (were in mockData, not shown):

| Mock field | Status | Note |
|---|---|---|
| `vehicleCount` | Not in DB | Shown as "N/A" |
| `currentDensity` | Not in DB | Shown as "N/A" |
| `expectedImpact` | Not in DB | Replaced with Phase 4 note |
| `junctionName` | Not directly in AI rec | Resolved via junction lookup |

---

## 8. Loading / Error / Empty States

### Loading State
While `getAiRecommendations` is fetching:
- The full page shows a spinning `RefreshCw` icon
- Text: "Loading recommendations…"

### Error State
If the API request fails (network error, server down):
- `AlertCircle` icon shown in red
- Error message from `apiFetch`: e.g. "Cannot connect to SignalAI backend"
- **Retry button** calls `refetchRecs()` again

### Empty State (per tab)
If a tab has zero recommendations:
- `Inbox` icon with text: "No {tab} recommendations."
- This is real — if the DB has no APPROVED records, the approved tab is empty.

### Action Error Banner
If Approve or Reject API call fails:
- An inline error banner appears above the split pane
- Text: "Approval failed: {api error}" or "Rejection failed: {api error}"
- Clears automatically on next action or tab switch

---

## 9. CRUD Actions Supported

| Action | Backend support | Connected | Notes |
|---|---|---|---|
| View recommendations | GET /api/ai-recommendations | YES | All tabs + filters |
| Approve (PENDING → APPROVED) | PUT /api/ai-recommendations/{id} | YES | Updates DB, refetches list |
| Reject (PENDING → REJECTED) | PUT /api/ai-recommendations/{id} | YES | Saves rejection_reason to DB |
| Refresh list | GET /api/ai-recommendations | YES | Manual refresh button (⟳) |
| Create recommendation | POST /api/ai-recommendations | NOT CONNECTED | No create form in UI; Phase 4 |
| Delete recommendation | DELETE /api/ai-recommendations/{id} | NOT CONNECTED | Not in Decision Queue UI |

### Approve flow:
1. User clicks "Approve & Execute"
2. Confirmation modal shown
3. User clicks "Confirm Execution"
4. `updateAiRecommendation(id, { status: 'APPROVED', reviewed_by: 1 })` called
5. On success: modal closes, list refetched from API, next PENDING auto-selected
6. On failure: modal stays open, error banner shows

### Reject flow:
1. User clicks "Reject"
2. Rejection modal shown with radio reason + optional text area
3. User clicks "Submit Rejection"
4. `updateAiRecommendation(id, { status: 'REJECTED', reviewed_by: 1, rejection_reason: '...' })` called
5. On success: modal closes, list refetched, next PENDING auto-selected
6. On failure: modal stays open, error banner shows

---

## 10. Phase 4 Note (reviewed_by)

The `reviewed_by` field is currently hardcoded to user id=1 (J. Sharma) because
JWT authentication is not yet implemented.

When Phase 4 adds JWT, replace with:

```js
reviewed_by: currentUser.id   // from JWT token / auth context
```

---

## 11. Testing Performed

### API Tests (curl)
| Test | Result |
|---|---|
| GET /api/ai-recommendations | PASS — 6 records |
| GET /api/ai-recommendations?status=PENDING | PASS — 4 records |
| GET /api/ai-recommendations?status=APPROVED | PASS — 1 record |
| GET /api/ai-recommendations?status=REJECTED | PASS — 1 record |
| GET /api/ai-recommendations/1 | PASS — full record returned |
| GET /api/ai-recommendations/9999 | PASS — 404 returned |
| PUT with invalid status | PASS — 422 returned |
| POST test rec → PUT approve → DELETE | PASS — full lifecycle cycle |

### Build
| Test | Result |
|---|---|
| npm run build | PASS — 0 errors |

### Regression
| Page | Result |
|---|---|
| Health endpoints | PASS |
| Dashboard (traffic summary) | PASS — 23,048 records |
| TrafficMap (junctions) | PASS — 8 junctions |
| Analytics (traffic records) | PASS |
| AdminUsers (users) | PASS — 6 users |
| DecisionQueue (new) | PASS — real API data |

### Mock Data Removal
| Check | Result |
|---|---|
| `from.*mockData` in DecisionQueue.jsx | PASS — not found |
| mockData.js still intact (other pages) | PASS — 229 lines untouched |

---

## 12. Database Verification

| Table | Before | After | Delta |
|---|---|---|---|
| traffic_records | 23,048 | **23,048** | 0 |
| ai_recommendations | 6 | 6 | 0 |
| signal_timings | 1 | 1 | 0 |
| emergency_routes | 3 | 3 | 0 |
| operator_logs | 6 | 6 | 0 |
| users | 6 | 6 | 0 |
| junctions | 8 | 8 | 0 |

> One test record (id=13) was created, verified, and deleted during testing.
> No original records were modified.

**traffic_records before = 23,048**
**traffic_records after  = 23,048**

---

## 13. Known Limitations

| # | Limitation | Resolution |
|---|---|---|
| 1 | `reviewed_by` hardcoded to user id=1 | Replace with JWT user ID in Phase 4 |
| 2 | `vehicleCount`, `currentDensity`, `expectedImpact` show N/A | Not in DB — would need rule-based AI engine to populate |
| 3 | No "Create Recommendation" form | Not in original UI — Phase 4 scope |
| 4 | No operator log written on approve/reject | Operator logs API exists — wire in Phase 4 with auth |
| 5 | Junction resolution requires second API call | `getJunctions()` (8 rows) — negligible; cached by useApi |

---

## 14. Next Recommended Phase

**Phase 4 tasks for Decision Queue:**

1. Replace `reviewed_by: 1` with actual JWT authenticated user ID
2. Write to `operator_logs` on every approve/reject action
3. Add "Create Recommendation" form (manual entry for operators)
4. Show real `vehicleCount` and `currentDensity` by joining `traffic_records`
5. Connect real-time signal timing change via `POST /api/signal-timings` after approval
6. Add optimistic UI updates (instant local update before API confirms)

