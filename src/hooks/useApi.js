/**
 * src/hooks/useApi.js
 * =====================
 * Generic hook for calling the API service.
 * Manages loading, error, and data state.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useApi(getJunctions);
 *
 * IMPORTANT: apiFn and args are captured via refs so that inline arrow
 * functions passed from components (e.g. `() => getAiRecommendations(...)`)
 * do NOT cause the effect to re-fire on every render.
 *
 * The initial fetch runs once on mount. Use `refetch()` to trigger manually.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * @param {Function} apiFn  - async function from src/services/api.js
 * @param {any[]}    args   - arguments forwarded to apiFn (stable array or
 *                           omit if apiFn already closes over its params)
 * @param {boolean}  skip   - if true, skip the initial fetch
 */
export function useApi(apiFn, args = [], skip = false) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError]     = useState(null);

  // Store latest apiFn and args in refs so the fetch callback is always
  // up-to-date but never changes its own identity — preventing infinite loops
  // caused by inline arrow functions recreated on every render.
  const apiFnRef = useRef(apiFn);
  const argsRef  = useRef(args);
  apiFnRef.current = apiFn;
  argsRef.current  = args;

  // `fetch` is stable — created once, reads latest fn/args from refs.
  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    const result = await apiFnRef.current(...argsRef.current);
    if (result.error) {
      setError(result.error);
      setData(null);
    } else {
      setData(result.data);
    }
    setLoading(false);
  }, []); // ← intentionally empty: fetch identity never changes

  // Fire once on mount (skip=false). Does NOT re-fire when apiFn changes.
  useEffect(() => {
    if (!skip) fetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip]); // fetch is stable so listing it is fine, but skip is the gate

  return { data, loading, error, refetch: fetch };
}
