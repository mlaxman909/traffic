/**
 * src/services/api.js
 * =====================
 * SignalAI Frontend API Service Layer
 *
 * All fetch() calls go through this file — NEVER directly in components.
 * Returns { data, error, status } — never throws.
 *
 * Base URL: VITE_API_BASE_URL (.env → http://localhost:8000)
 *
 * Verified endpoints:
 *   GET    /api/health
 *   GET    /api/health/database
 *
 *   GET    /api/users
 *   GET    /api/users/{id}
 *   POST   /api/users            → create user
 *   PUT    /api/users/{id}       → update user
 *   DELETE /api/users/{id}       → delete user
 *
 *   GET    /api/junctions
 *   GET    /api/junctions/{id}
 *   POST   /api/junctions        → create junction
 *   PUT    /api/junctions/{id}   → update junction
 *   DELETE /api/junctions/{id}   → delete junction
 *
 *   GET    /api/traffic-records
 *   GET    /api/traffic-records/summary
 *   GET    /api/traffic-records/{id}
 *
 *   GET    /api/ai-recommendations
 *   GET    /api/ai-recommendations/{id}
 *   PUT    /api/ai-recommendations/{id}  → approve / reject
 */


// Use Vite proxy in dev so all requests go to same origin (no CORS issues).
// Vite forwards /api/* → http://127.0.0.1:8000/api/*
const BASE_URL = '';

// ── Core fetch wrapper ──────────────────────────────────────────────────────

/**
 * Central fetch wrapper.
 * - Merges default headers
 * - Handles 204 No Content (DELETE responses)
 * - Returns { data, error, status } — never throws
 */
async function apiFetch(path, options = {}) {
  try {
    const token = localStorage.getItem('token');
    const headers = { 
      'Content-Type': 'application/json', 
      Accept: 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };

    const res = await fetch(`${BASE_URL}${path}`, {
      headers,
      ...options,
    });

    // 204 No Content (successful DELETE) — no body to parse
    if (res.status === 204) {
      return { data: null, error: null, status: 204 };
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      
      // Handle 401 Unauthorized globally
      if (res.status === 401) {
        localStorage.removeItem('token');
        // Dispatch an event so the AuthContext can log out without circular dependencies
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
      
      return {
        data: null,
        error: body.detail || `Server error ${res.status}`,
        status: res.status,
      };
    }

    const data = await res.json();
    return { data, error: null, status: res.status };
  } catch {
    return {
      data: null,
      error: 'Cannot connect to SignalAI backend. Is the server running?',
      status: 0,
    };
  }
}

// ── Health ──────────────────────────────────────────────────────────────────

/** GET /api/health */
export async function getHealth() {
  return apiFetch('/api/health');
}

/** GET /api/health/database */
export async function getDatabaseHealth() {
  return apiFetch('/api/health/database');
}

// ── Auth ────────────────────────────────────────────────────────────────────

/**
 * POST /api/auth/login
 * Body: URL encoded form data (OAuth2PasswordRequestForm)
 */
export async function login(username, password) {
  // Trim whitespace — trailing spaces in email are a common cause of 401 errors
  const cleanUsername = (username || '').trim();
  const cleanPassword = (password || '').trim();

  const formData = new URLSearchParams();
  formData.append('username', cleanUsername);
  formData.append('password', cleanPassword);

  const res = await fetch(`/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Login failed');
  }

  return res.json();
}

/**
 * GET /api/auth/me
 */
export async function getMe() {
  const { data, error } = await apiFetch('/api/auth/me');
  if (error) throw new Error(error);
  return data;
}

// ── Users ───────────────────────────────────────────────────────────────────

/**
 * GET /api/users
 * Returns: [{ id, name, email, role, status, district }]
 */
export async function getUsers() {
  return apiFetch('/api/users');
}

/**
 * GET /api/users/{id}
 * Returns: { id, name, email, role, status, district, created_at, last_login }
 */
export async function getUser(id) {
  return apiFetch(`/api/users/${id}`);
}

/**
 * POST /api/users
 * Body: { name, email, role, status, district }
 * Returns 201 + created user | 409 if email duplicate
 */
export async function createUser(payload) {
  return apiFetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({
      name:          payload.name,
      email:         payload.email,
      role:          payload.role,
      status:        payload.status || 'ACTIVE',
      district:      payload.district || null,
      password_hash: 'placeholder_hash',  // Phase 4 will hash properly
    }),
  });
}

/**
 * PUT /api/users/{id}
 * Body: partial { name?, email?, role?, status?, district? }
 * Returns 200 + updated user | 404 | 409
 */
export async function updateUser(id, payload) {
  return apiFetch(`/api/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

/**
 * DELETE /api/users/{id}
 * Returns 204 No Content | 404
 */
export async function deleteUser(id) {
  return apiFetch(`/api/users/${id}`, { method: 'DELETE' });
}

// ── Junctions ───────────────────────────────────────────────────────────────

/**
 * GET /api/junctions
 * Returns: [{ id, junction_code, name, status, traffic_density, latitude, longitude }]
 */
export async function getJunctions() {
  return apiFetch('/api/junctions');
}

/**
 * GET /api/junctions/{id}
 */
export async function getJunction(id) {
  return apiFetch(`/api/junctions/${id}`);
}

/**
 * POST /api/junctions
 * Body: { junction_code, name, latitude?, longitude?, status?, traffic_density?,
 *         current_green_time?, weather_condition? }
 * Returns 201 + created junction | 409 if code duplicate
 */
export async function createJunction(payload) {
  return apiFetch('/api/junctions', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * PUT /api/junctions/{id}
 * Body: partial junction fields (all optional)
 * Returns 200 + updated junction | 404
 */
export async function updateJunction(id, payload) {
  return apiFetch(`/api/junctions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

/**
 * DELETE /api/junctions/{id}
 * Returns 204 No Content | 404
 * NOTE: CASCADE is enabled — deletes associated traffic_records too.
 */
export async function deleteJunction(id) {
  return apiFetch(`/api/junctions/${id}`, { method: 'DELETE' });
}

// ── Traffic Records ─────────────────────────────────────────────────────────

/**
 * GET /api/traffic-records
 * Params: { limit, skip, junction_id, traffic_level, from_date, to_date }
 */
export async function getTrafficRecords({ limit = 100, skip = 0, junction_id, traffic_level, from_date, to_date } = {}) {
  const params = new URLSearchParams();
  params.set('limit', limit);
  params.set('skip', skip);
  if (junction_id)   params.set('junction_id', junction_id);
  if (traffic_level) params.set('traffic_level', traffic_level);
  if (from_date)     params.set('from_date', from_date);
  if (to_date)       params.set('to_date', to_date);
  return apiFetch(`/api/traffic-records?${params}`);
}

/**
 * GET /api/traffic-records/summary
 * Returns per-junction aggregates from all 23,048 records
 */
export async function getTrafficSummary() {
  return apiFetch('/api/traffic-records/summary');
}

/**
 * GET /api/traffic-records/{id}
 */
export async function getTrafficRecord(id) {
  return apiFetch(`/api/traffic-records/${id}`);
}

// ── AI Recommendations ───────────────────────────────────────────────────────

/**
 * GET /api/ai-recommendations
 *
 * Returns the full list of AI recommendations ordered by created_at descending.
 *
 * Optional filters (all omitted → returns all):
 *   @param {string}  status    - 'PENDING' | 'APPROVED' | 'REJECTED'
 *   @param {string}  severity  - 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
 *   @param {number}  junction_id - filter by junction DB id
 *   @param {number}  limit     - max records (default 100)
 *   @param {number}  skip      - offset for pagination (default 0)
 *
 * API field reference (returned by FastAPI):
 *   id, junction_id, traffic_record_id,
 *   recommendation_text, reason,
 *   current_green_time, suggested_green_time,
 *   severity, status,
 *   created_at, reviewed_at, reviewed_by, rejection_reason
 */
export async function getAiRecommendations({ status, severity, junction_id, limit = 100, skip = 0 } = {}) {
  const params = new URLSearchParams();
  params.set('limit', limit);
  params.set('skip', skip);
  if (status)      params.set('status', status);
  if (severity)    params.set('severity', severity);
  if (junction_id) params.set('junction_id', junction_id);
  return apiFetch(`/api/ai-recommendations?${params}`);
}

/**
 * GET /api/ai-recommendations/{id}
 * Returns a single recommendation by its database ID.
 */
export async function getAiRecommendation(id) {
  return apiFetch(`/api/ai-recommendations/${id}`);
}

/**
 * PUT /api/ai-recommendations/{id}
 *
 * Updates a recommendation's lifecycle state (approve or reject).
 * The backend auto-sets reviewed_at when status changes from PENDING.
 *
 * Body fields (all optional — only changed fields required):
 *   @param {number} id        - the recommendation's database ID
 *   @param {object} payload   - fields to update, e.g.:
 *     { status: 'APPROVED', reviewed_by: 1 }
 *     { status: 'REJECTED', reviewed_by: 1, rejection_reason: 'Unsafe conditions' }
 *
 * Returns 200 + updated recommendation | 404 | 422
 */
export async function updateAiRecommendation(id, payload) {
  return apiFetch(`/api/ai-recommendations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

// ── Emergency Routes ────────────────────────────────────────────────────────

/**
 * GET /api/emergency-routes
 */
export async function getEmergencyRoutes(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`/api/emergency-routes${query ? `?${query}` : ''}`);
}

/**
 * POST /api/emergency-routes
 */
export async function createEmergencyRoute(payload) {
  return apiFetch('/api/emergency-routes', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * PUT /api/emergency-routes/{id}
 */
export async function updateEmergencyRoute(id, payload) {
  return apiFetch(`/api/emergency-routes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

// ── Operator Logs ───────────────────────────────────────────────────────────

/**
 * GET /api/operator-logs
 */
export async function getOperatorLogs(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`/api/operator-logs${query ? `?${query}` : ''}`);
}

// ── AI Recommendations Generate ───────────────────────────────────────────────

/**
 * POST /api/ai-recommendations/generate
 */
export async function generateAiRecommendations() {
  return apiFetch('/api/ai-recommendations/generate', { method: 'POST' });
}

// ── Road Network (OpenStreetMap) ─────────────────────────────────────────────
//
// Data source: OpenStreetMap contributors (ODbL License)
// https://www.openstreetmap.org/copyright
//
// IMPORTANT: Road network data contains ONLY geographic attributes (road geometry,
// name, type, lanes, speed limit). It does NOT contain traffic volume, vehicle
// counts, or congestion data. Traffic data comes from /api/traffic-records.

/**
 * GET /api/road-network/geojson
 *
 * Returns a GeoJSON FeatureCollection of road segments.
 * Supports filtering by highway_type for performance.
 *
 * @param {Object} params
 * @param {string} [params.highway_type] - e.g. 'primary', 'secondary', 'trunk', 'motorway'
 * @param {number} [params.limit=500]    - Max features (default 500, max 2000)
 * @param {number} [params.skip=0]       - Offset
 * @param {boolean} [params.oneway]      - Filter one-way roads
 * @param {boolean} [params.has_name]    - Filter named roads only
 *
 * Returns GeoJSON FeatureCollection with OSM attribution.
 * Each Feature.properties includes: id, osm_id, highway_type, road_name, etc.
 */
export async function getRoadNetworkGeoJSON({
  highway_type,
  limit = 500,
  skip = 0,
  oneway,
  has_name,
} = {}) {
  const params = new URLSearchParams();
  params.set('limit', limit);
  params.set('skip', skip);
  if (highway_type !== undefined) params.set('highway_type', highway_type);
  if (oneway !== undefined)       params.set('oneway', oneway);
  if (has_name !== undefined)     params.set('has_name', has_name);
  return apiFetch(`/api/road-network/geojson?${params}`);
}

/**
 * GET /api/road-network
 *
 * Returns paginated list of road segments WITHOUT geometry (for tables/lists).
 * Use getRoadNetworkGeoJSON() for map rendering.
 *
 * @param {Object} params
 * @param {string} [params.highway_type]
 * @param {string} [params.road_name]    - Partial name search (case-insensitive)
 * @param {number} [params.limit=100]
 * @param {number} [params.skip=0]
 */
export async function getRoadNetwork({
  highway_type,
  road_name,
  oneway,
  limit = 100,
  skip = 0,
} = {}) {
  const params = new URLSearchParams();
  params.set('limit', limit);
  params.set('skip', skip);
  if (highway_type) params.set('highway_type', highway_type);
  if (road_name)    params.set('road_name', road_name);
  if (oneway !== undefined) params.set('oneway', oneway);
  return apiFetch(`/api/road-network?${params}`);
}

/**
 * GET /api/road-network/{id}
 * Returns a single road segment with full geometry.
 */
export async function getRoadById(id) {
  return apiFetch(`/api/road-network/${id}`);
}

/**
 * GET /api/road-network/stats
 * Returns dataset statistics (total count, highway breakdown, etc.)
 */
export async function getRoadNetworkStats() {
  return apiFetch('/api/road-network/stats');
}

