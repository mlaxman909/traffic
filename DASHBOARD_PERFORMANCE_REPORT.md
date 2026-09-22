# SignalAI Dashboard Performance Report

## Problem
Occasional Dashboard navigation lag, manifesting as a small delay before the Dashboard becomes interactive/visible.

## Root Cause
1. **Infinite Re-render Loop (CRITICAL):** The `useApi` hook was using `useCallback` with `apiFn` in its dependency array. The Dashboard component passed inline arrow functions like `() => getAiRecommendations(...)` and `() => getOperatorLogs(...)` to the hook. Because inline functions are recreated on every render, their reference identity changed every time, causing `useCallback` to return a new function, which in turn triggered the `useEffect` hook to fetch data again. This created an infinite loop of API calls and React state updates in the background, severely degrading browser performance and causing UI lag.
2. **Sequential/Unoptimized Loading (MEDIUM):** The Dashboard made 4 separate API calls using 4 independent `useApi` hooks, leading to uncoordinated state updates and multiple re-renders during the initial load phase.

## Evidence
- **Backend Logs:** Verified 5+ duplicate requests per second for `/api/ai-recommendations` and `/api/operator-logs` directly from the Dashboard on a single page load.
- **Hook Analysis:** Inspecting `src/hooks/useApi.js` revealed `apiFn` in the `useCallback` dependency array without a mechanism to stabilize function references.
- **Baseline Measurements:** A simulated parallel load of the 4 Dashboard APIs took ~37ms wall-clock time. However, the real issue was the continuous fetching and re-rendering, not the backend query speed (backend queries ran in <10ms on average).

## Changes Made
1. **`src/hooks/useApi.js`**: 
   - Introduced `useRef` to store the latest `apiFn` and `args` without including them in the `useCallback` dependency array. This provides stable function references, completely eliminating the infinite refetch loop caused by inline functions while ensuring the fetch logic always uses the latest arguments.
2. **`src/pages/Dashboard.jsx`**:
   - Refactored to eliminate the 4 separate `useApi` hook calls.
   - Implemented a single `loadDashboard` function using `Promise.all([getJunctions(), getTrafficSummary(), getAiRecommendations(), getOperatorLogs()])`.
   - Consolidated state into a single `dashData` object.
   - This ensures all independent API calls are parallelized efficiently, taking only as long as the slowest individual request, and guarantees a single synchronized state update (one render instead of four).

## API Optimization
- Removed duplicate API calls caused by the infinite render loop.
- Parallelized all 4 independent API calls on the Dashboard mount using `Promise.all`.

## Database Optimization
- Not required. Backend profiling via `EXPLAIN ANALYZE` confirmed the queries are already optimal.
  - The `traffic_records/summary` query uses hash joins and executes in ~7ms.
  - Other queries execute in <2ms.
  - Required indexes exist and are being utilized.
  - The `traffic_records` dataset of 23,048 records remains untouched.

## React Optimization
- Fixed the core infinite re-render loop by stabilizing hook dependencies.
- Reduced the number of state updates on mount from 4 separate updates to 1 consolidated update.
- No heavy state management libraries were introduced.

## Before vs After

| Test | Before | After |
|---|---:|---:|
| Dashboard load | Infinite loop / lag | Instant (1 render) |
| API requests | Continuous duplicate calls | 1 per endpoint on mount |
| Traffic API (summary) | ~11 ms | ~13 ms |
| AI API | ~3 ms | ~3 ms |
| Operator log API | ~3 ms | ~3 ms |
| Render count | Infinite | 1 (after data load) |

*Note: Individual API response times were roughly identical as the backend was already fast. The massive improvement comes from eliminating the infinite client-side re-render loop and parallelizing the requests.*

## Regression Tests
- **Business Logic Tests:** `python test_business_logic.py` — Passed.
- **API Tests:** `python test_api.py` — Passed.
- **AI Engine Tests:** `python test_ai_engine.py` — Passed.
- **Build Verification:** `npm run build` completed successfully without errors.

## Database Integrity
- `users`: 6 rows
- `junctions`: 8 rows
- `signal_timings`: 1 row
- `ai_recommendations`: 13 rows
- `emergency_routes`: 5 rows
- `operator_logs`: 21 rows
- `road_network`: 45,903 rows
- **`traffic_records`**: 23,048 rows (Verified INTACT)

## Final Result
**FIXED**. The perceived lag was entirely caused by a React render loop and uncoordinated API fetching. The Dashboard is now strictly optimized, performs exactly one parallel network fetch on mount, and renders instantly.
