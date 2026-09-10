-- ============================================================
-- SignalAI Seed Data
-- ============================================================
-- Purpose:  Populate the signalai database with demo data
--           sourced from the Phase 1 mockData.js prototype.
-- Phase:    2 — Database Foundation
--
-- WARNING: This is DEMO / PROTOTYPE data only.
--          It must NOT be used in any production system.
--          Replace with real data before public deployment.
--
-- How to apply:
--   1. Apply schema.sql first
--   2. psql -U postgres -d signalai -f seed.sql
-- ============================================================


-- ── Seed: users ──────────────────────────────────────────────────────────────
-- Source: mockData.js → users array
-- Passwords: all set to placeholder hash (real auth in Phase 3)
-- The placeholder hash below is NOT a real password hash.

INSERT INTO users (name, email, password_hash, role, status, district) VALUES
    -- Demo operator (matches Phase 1 demo login)
    ('J. Sharma',
     'j.sharma@signalai.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'TRAFFIC_OPERATOR', 'ACTIVE', 'North'),

    ('R. Mehta',
     'r.mehta@signalai.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'SYSTEM_ADMINISTRATOR', 'ACTIVE', NULL),

    ('P. Verma',
     'p.verma@signalai.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'TRAFFIC_OPERATOR', 'ACTIVE', 'South'),

    ('S. Gupta',
     's.gupta@municipal.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'MUNICIPAL_AUTHORITY', 'ACTIVE', NULL),

    ('A. Khan',
     'a.khan@emergency.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'EMERGENCY_SERVICE', 'ACTIVE', 'North'),

    ('K. Singh',
     'k.singh@signalai.gov.in',
     '$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL',
     'TRAFFIC_OPERATOR', 'INACTIVE', 'East')
ON CONFLICT (email) DO NOTHING;


-- ── Seed: junctions ──────────────────────────────────────────────────────────
-- Source: mockData.js → junctions array (8 junctions)
-- Status mapping: red→HIGH, yellow→MODERATE, green→NORMAL

INSERT INTO junctions (junction_code, name, latitude, longitude, status, traffic_density, current_green_time, weather_condition) VALUES
    ('J-101', 'Genda Circle',         22.316440, 73.166340, 'HIGH',     96, 45, 'Light Rain, 27°C'),
    ('J-102', 'Kala Ghoda Circle',    22.308250, 73.181800, 'HIGH',     88, 40, 'Clear, 29°C'),
    ('J-103', 'Chakli Circle',        22.315050, 73.155890, 'MODERATE', 62, 35, 'Cloudy, 28°C'),
    ('J-104', 'Fatehgunj Circle',     22.323600, 73.184300, 'MODERATE', 55, 30, 'Clear, 30°C'),
    ('J-105', 'Amit Nagar Circle',    22.333170, 73.200150, 'NORMAL',   28, 30, 'Clear, 30°C'),
    ('J-106', 'Susen Circle',         22.266200, 73.193200, 'NORMAL',   18, 25, 'Clear, 30°C'),
    ('J-107', 'Muktanand Circle',     22.320400, 73.198300, 'NORMAL',   12, 25, 'Clear, 29°C'),
    ('J-108', 'Akota Circle',         22.299500, 73.163300, 'HIGH',     92, 50, 'Humid, 31°C')
ON CONFLICT (junction_code) DO NOTHING;


-- ── Seed: traffic_records ─────────────────────────────────────────────────────
-- Source: mockData.js → junctions array (vehicles, density values)
-- One snapshot per junction representing the current Phase 1 state.

INSERT INTO traffic_records (junction_id, vehicles, traffic_level, congestion_percentage, recorded_at)
SELECT
    j.id,
    v.vehicles,
    v.traffic_level::traffic_level,
    v.congestion_pct,
    NOW() - INTERVAL '10 minutes'
FROM junctions j
JOIN (VALUES
    ('J-101', 184, 'CRITICAL', 96),
    ('J-102', 162, 'HIGH',     88),
    ('J-103',  98, 'MODERATE', 62),
    ('J-104',  87, 'MODERATE', 55),
    ('J-105',  42, 'LOW',      28),
    ('J-106',  26, 'LOW',      18),
    ('J-107',  19, 'LOW',      12),
    ('J-108', 175, 'CRITICAL', 92)
) AS v(code, vehicles, traffic_level, congestion_pct)
    ON j.junction_code = v.code;


-- ── Seed: signal_timings ─────────────────────────────────────────────────────
-- Source: mockData.js → recommendations (AI-9035 was approved for J-104)
-- Represents the one historical timing change from mock data.

INSERT INTO signal_timings (junction_id, previous_green_time, new_green_time, reason, changed_by, changed_at)
SELECT
    j.id,
    30,
    36,
    'Preventive adjustment: Moderate evening peak building ahead of schedule. Recommendation AI-9035 applied.',
    u.id,
    NOW() - INTERVAL '1 hour'
FROM junctions j, users u
WHERE j.junction_code = 'J-104'
  AND u.email = 'j.sharma@signalai.gov.in';


-- ── Seed: ai_recommendations ─────────────────────────────────────────────────
-- Source: mockData.js → recommendations array (6 items)

INSERT INTO ai_recommendations (
    junction_id, recommendation_text, reason,
    current_green_time, suggested_green_time, severity, status, created_at
)
SELECT
    j.id,
    v.rec_text,
    v.reason,
    v.current_gt,
    v.suggested_gt,
    v.severity::recommendation_severity,
    v.status::recommendation_status,
    NOW() - v.offset_interval
FROM junctions j
JOIN (VALUES
    ('J-101',
     'Increase N/S green phase duration by +20 seconds to reduce Northbound queue at peak.',
     'Traffic density at Junction J-101 is 96% — significantly above network average of 52%. Queue of ~400m on Northbound approach.',
     45, 65, 'CRITICAL', 'PENDING',   INTERVAL '18 minutes'),

    ('J-102',
     'Increase E/W green phase duration by +12 seconds.',
     'Eastbound vehicles experiencing prolonged wait times due to insufficient green time relative to current peak load.',
     40, 52, 'HIGH',     'PENDING',   INTERVAL '25 minutes'),

    ('J-103',
     'Adjust signal offset by +8 seconds to synchronize with J-104 corridor.',
     'Synchronize offset timing with adjacent Junction J-104 to create a coordinated green wave on the southbound corridor.',
     35, 35, 'MEDIUM',   'PENDING',   INTERVAL '40 minutes'),

    ('J-108',
     'Temporarily increase green time by +15 seconds for 10 signal cycles.',
     'Heavy congestion near the railway station due to train arrival. Historic patterns confirm peak load lasts approximately 15 minutes.',
     50, 65, 'CRITICAL', 'PENDING',   INTERVAL '1 hour 2 minutes'),

    ('J-104',
     'Increase N/S green phase by +6 seconds.',
     'Moderate evening peak building ahead of schedule. Preventive adjustment recommended.',
     30, 36, 'MEDIUM',   'APPROVED',  INTERVAL '1 hour 30 minutes'),

    ('J-106',
     'Reduce cycle time by 5 seconds.',
     'Low traffic detected. Reducing cycle time will improve overall network rhythm.',
     25, 20, 'LOW',      'REJECTED',  INTERVAL '2 hours 5 minutes')
) AS v(code, rec_text, reason, current_gt, suggested_gt, severity, status, offset_interval)
    ON j.junction_code = v.code;

-- Mark the approved and rejected ones with reviewer info
UPDATE ai_recommendations ar
SET
    reviewed_at = created_at + INTERVAL '30 minutes',
    reviewed_by = (SELECT id FROM users WHERE email = 'j.sharma@signalai.gov.in')
WHERE ar.status IN ('APPROVED', 'REJECTED');

UPDATE ai_recommendations ar
SET rejection_reason = 'Inaccurate traffic data — sensor reading appears anomalous for this time of day.'
WHERE ar.status = 'REJECTED';


-- ── Seed: emergency_routes ────────────────────────────────────────────────────
-- Source: mockData.js → emergencyHistory array (3 items)

INSERT INTO emergency_routes (
    emergency_type, vehicle_id,
    origin_junction_id, destination_junction_id,
    route_description,
    authorization_status, status,
    started_at, completed_at,
    created_by, created_at
)
SELECT
    v.etype::emergency_type,
    v.vehicle_id,
    orig.id,
    dest.id,
    v.route_desc,
    'AUTHORIZED'::authorization_status,
    'COMPLETED'::route_status,
    v.started,
    v.completed,
    (SELECT id FROM users WHERE email = 'j.sharma@signalai.gov.in'),
    v.started
FROM (VALUES
    ('AMBULANCE',    'AMB-07',   'J-101', 'J-106', 'J-101 → J-103 → J-106',
     NOW() - INTERVAL '1 hour 46 minutes', NOW() - INTERVAL '1 hour 30 minutes'),
    ('FIRE_SERVICE', 'FIRE-E12', 'J-104', 'J-108', 'J-104 → J-108',
     NOW() - INTERVAL '1 day 5 hours',    NOW() - INTERVAL '1 day 4 hours 40 minutes'),
    ('POLICE',       'POL-P01',  'J-102', 'J-101', 'J-102 → J-101',
     NOW() - INTERVAL '1 day 4 hours',    NOW() - INTERVAL '1 day 3 hours 45 minutes')
) AS v(etype, vehicle_id, orig_code, dest_code, route_desc, started, completed)
JOIN junctions orig ON orig.junction_code = v.orig_code
JOIN junctions dest ON dest.junction_code = v.dest_code;


-- ── Seed: operator_logs ───────────────────────────────────────────────────────
-- Source: mockData.js → recentActivity array (5 items)

INSERT INTO operator_logs (user_id, action, entity_type, entity_id, description, created_at)
SELECT
    (SELECT id FROM users WHERE email = 'j.sharma@signalai.gov.in'),
    v.action,
    v.entity_type,
    NULL,
    v.description,
    v.log_time
FROM (VALUES
    ('SUBMIT_RECOMMENDATION', 'ai_recommendation',
     'Recommendation AI-9042 submitted for J-101',           NOW() - INTERVAL '18 minutes'),
    ('APPROVE_RECOMMENDATION', 'ai_recommendation',
     'Operator approved recommendation AI-9036 for J-104',   NOW() - INTERVAL '25 minutes'),
    ('ACTIVATE_EMERGENCY_ROUTE', 'emergency_route',
     'Emergency Route ER-041 authorized — Ambulance AMB-07', NOW() - INTERVAL '45 minutes'),
    ('SENSOR_ALERT', 'junction',
     'Sensor offline alert: J-107 (resolved)',                NOW() - INTERVAL '1 hour 2 minutes'),
    ('APPROVE_RECOMMENDATION', 'ai_recommendation',
     'Recommendation AI-9035 applied to J-104',              NOW() - INTERVAL '1 hour 30 minutes')
) AS v(action, entity_type, description, log_time);


-- ── Verification query ─────────────────────────────────────────────────────────
-- Run this after seeding to confirm row counts:
SELECT
    'users'              AS table_name, COUNT(*) AS row_count FROM users            UNION ALL
SELECT 'junctions',                                            COUNT(*) FROM junctions         UNION ALL
SELECT 'traffic_records',                                      COUNT(*) FROM traffic_records    UNION ALL
SELECT 'signal_timings',                                       COUNT(*) FROM signal_timings     UNION ALL
SELECT 'ai_recommendations',                                   COUNT(*) FROM ai_recommendations UNION ALL
SELECT 'emergency_routes',                                     COUNT(*) FROM emergency_routes   UNION ALL
SELECT 'operator_logs',                                        COUNT(*) FROM operator_logs;

-- Expected output:
-- users              | 6
-- junctions          | 8
-- traffic_records    | 8
-- signal_timings     | 1
-- ai_recommendations | 6
-- emergency_routes   | 3
-- operator_logs      | 5

-- ── End of seed.sql ────────────────────────────────────────────────────────────
