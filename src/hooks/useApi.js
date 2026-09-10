/**
 * src/hooks/useApi.js
 * =====================
 * Generic hook for calling the API service.
 * Manages loading, error, and data state.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useApi(getJunctions);
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * @param {Function} apiFn  - async function from src/services/api.js
 * @param {any[]}    args   - arguments forwarded to apiFn
 * @param {boolean}  skip   - if true, skip the initial fetch
 */
export function useApi(apiFn, args = [], skip = false) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError]     = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    const result = await apiFn(...args);
    if (result.error) {
      setError(result.error);
      setData(null);
    } else {
      setData(result.data);
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiFn, JSON.stringify(args)]);

  useEffect(() => {
    if (!skip) fetch();
  }, [fetch, skip]);

  return { data, loading, error, refetch: fetch };
}
