-- ============================================================
-- SignalAI Database Schema
-- ============================================================
-- Database: signalai (PostgreSQL 16+)
-- Purpose:  Smart Traffic Signal Optimization Platform
-- Phase:    2 — Database Foundation
--
-- How to apply this schema:
--   1. Create the database: CREATE DATABASE signalai;
--   2. Connect to it: \c signalai
--   3. Run this file: \i /path/to/schema.sql
--      OR via psql:   psql -U postgres -d signalai -f schema.sql
-- ============================================================


-- ── Clean slate (drop in reverse dependency order) ────────────────────────────
-- Uncomment these lines if you need to reset the database during development:
-- DROP TABLE IF EXISTS operator_logs      CASCADE;
-- DROP TABLE IF EXISTS emergency_routes   CASCADE;
-- DROP TABLE IF EXISTS ai_recommendations CASCADE;
-- DROP TABLE IF EXISTS signal_timings     CASCADE;
-- DROP TABLE IF EXISTS traffic_records    CASCADE;
-- DROP TABLE IF EXISTS junctions          CASCADE;
-- DROP TABLE IF EXISTS users              CASCADE;
-- DROP TYPE  IF EXISTS user_role, user_status,
--                      junction_status, traffic_level,
--                      recommendation_status, recommendation_severity,
--                      emergency_type, authorization_status, route_status CASCADE;


-- ── Enum Types ────────────────────────────────────────────────────────────────

CREATE TYPE user_role AS ENUM (
    'TRAFFIC_OPERATOR',
    'SYSTEM_ADMINISTRATOR',
    'MUNICIPAL_AUTHORITY',
    'EMERGENCY_SERVICE'
);

CREATE TYPE user_status AS ENUM (
    'ACTIVE',
    'INACTIVE'
);

CREATE TYPE junction_status AS ENUM (
    'NORMAL',
    'MODERATE',
    'HIGH',
    'CRITICAL'
);

CREATE TYPE traffic_level AS ENUM (
    'LOW',
    'MODERATE',
    'HIGH',
    'CRITICAL'
);

CREATE TYPE recommendation_severity AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);

CREATE TYPE recommendation_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED'
);

CREATE TYPE emergency_type AS ENUM (
    'AMBULANCE',
    'FIRE_SERVICE',
    'POLICE'
);

CREATE TYPE authorization_status AS ENUM (
    'PENDING',
    'AUTHORIZED',
    'REJECTED'
);

CREATE TYPE route_status AS ENUM (
    'PLANNED',
    'ACTIVE',
    'COMPLETED',
    'CANCELLED'
);


-- ── Table 1: users ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL          PRIMARY KEY,
    name          VARCHAR(100)    NOT NULL,
    email         VARCHAR(255)    NOT NULL UNIQUE,
    password_hash VARCHAR(255)    NOT NULL,
    role          user_role       NOT NULL DEFAULT 'TRAFFIC_OPERATOR',
    status        user_status     NOT NULL DEFAULT 'ACTIVE',
    district      VARCHAR(100),
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_login    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_email  ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role   ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users (status);

COMMENT ON TABLE  users                IS 'Authorized personnel who operate the SignalAI platform';
COMMENT ON COLUMN users.password_hash  IS 'Bcrypt hash — plaintext passwords are never stored';
COMMENT ON COLUMN users.district       IS 'City district this operator is assigned to';


-- ── Table 2: junctions ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS junctions (
    id                 SERIAL          PRIMARY KEY,
    junction_code      VARCHAR(20)     NOT NULL UNIQUE,
    name               VARCHAR(200)    NOT NULL,
    latitude           DOUBLE PRECISION,
    longitude          DOUBLE PRECISION,
    status             junction_status NOT NULL DEFAULT 'NORMAL',
    traffic_density    INTEGER         CHECK (traffic_density BETWEEN 0 AND 100),
    current_green_time INTEGER         CHECK (current_green_time >= 0),
    weather_condition  VARCHAR(100),
    created_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_junctions_code   ON junctions (junction_code);
CREATE INDEX IF NOT EXISTS idx_junctions_status ON junctions (status);

COMMENT ON TABLE  junctions               IS 'Monitored road intersections with traffic signals';
COMMENT ON COLUMN junctions.junction_code IS 'Short unique identifier, e.g. J-101';
COMMENT ON COLUMN junctions.traffic_density IS 'Current congestion percentage (0-100)';


-- ── Table 3: traffic_records ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS traffic_records (
    id                     SERIAL          PRIMARY KEY,
    junction_id            INTEGER         NOT NULL REFERENCES junctions(id) ON DELETE CASCADE,
    recorded_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    vehicles               INTEGER         CHECK (vehicles >= 0),
    traffic_level          traffic_level   NOT NULL DEFAULT 'LOW',
    congestion_percentage  INTEGER         CHECK (congestion_percentage BETWEEN 0 AND 100),
    created_at             TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traffic_junction   ON traffic_records (junction_id);
CREATE INDEX IF NOT EXISTS idx_traffic_recorded   ON traffic_records (recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_level      ON traffic_records (traffic_level);

COMMENT ON TABLE traffic_records IS 'Time-series traffic observations at each junction. Kaggle dataset will populate this table in Phase 3.';


-- ── Table 4: signal_timings ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS signal_timings (
    id                  SERIAL      PRIMARY KEY,
    junction_id         INTEGER     NOT NULL REFERENCES junctions(id) ON DELETE CASCADE,
    previous_green_time INTEGER     CHECK (previous_green_time >= 0),
    new_green_time      INTEGER     NOT NULL CHECK (new_green_time >= 1),
    reason              TEXT,
    changed_by          INTEGER     REFERENCES users(id) ON DELETE SET NULL,
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signal_junction ON signal_timings (junction_id);
CREATE INDEX IF NOT EXISTS idx_signal_changed  ON signal_timings (changed_at DESC);

COMMENT ON TABLE signal_timings IS 'Audit trail of every signal timing change. Operator must explicitly approve before entry is created.';


-- ── Table 5: ai_recommendations ───────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id                   SERIAL                   PRIMARY KEY,
    junction_id          INTEGER                  NOT NULL REFERENCES junctions(id) ON DELETE CASCADE,
    traffic_record_id    INTEGER                  REFERENCES traffic_records(id) ON DELETE SET NULL,
    recommendation_text  TEXT                     NOT NULL,
    reason               TEXT,
    current_green_time   INTEGER                  CHECK (current_green_time >= 0),
    suggested_green_time INTEGER                  CHECK (suggested_green_time >= 0),
    severity             recommendation_severity  NOT NULL DEFAULT 'MEDIUM',
    status               recommendation_status    NOT NULL DEFAULT 'PENDING',
    created_at           TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    reviewed_at          TIMESTAMPTZ,
    reviewed_by          INTEGER                  REFERENCES users(id) ON DELETE SET NULL,
    rejection_reason     TEXT
);

CREATE INDEX IF NOT EXISTS idx_rec_junction  ON ai_recommendations (junction_id);
CREATE INDEX IF NOT EXISTS idx_rec_status    ON ai_recommendations (status);
CREATE INDEX IF NOT EXISTS idx_rec_severity  ON ai_recommendations (severity);
CREATE INDEX IF NOT EXISTS idx_rec_created   ON ai_recommendations (created_at DESC);

COMMENT ON TABLE ai_recommendations IS 'AI-generated signal timing suggestions. MUST be approved by a human operator before any action is taken.';
COMMENT ON COLUMN ai_recommendations.status IS 'PENDING until an operator acts. AI never autonomously changes to APPROVED.';


-- ── Table 6: emergency_routes ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS emergency_routes (
    id                       SERIAL               PRIMARY KEY,
    emergency_type           emergency_type        NOT NULL,
    vehicle_id               VARCHAR(50)           NOT NULL,
    origin_junction_id       INTEGER               NOT NULL REFERENCES junctions(id) ON DELETE RESTRICT,
    destination_junction_id  INTEGER               NOT NULL REFERENCES junctions(id) ON DELETE RESTRICT,
    priority                 INTEGER               NOT NULL DEFAULT 1 CHECK (priority >= 1),
    route_description        TEXT,
    estimated_duration       INTEGER               CHECK (estimated_duration >= 1),
    authorization_status     authorization_status  NOT NULL DEFAULT 'PENDING',
    status                   route_status          NOT NULL DEFAULT 'PLANNED',
    started_at               TIMESTAMPTZ,
    completed_at             TIMESTAMPTZ,
    created_by               INTEGER               REFERENCES users(id) ON DELETE SET NULL,
    created_at               TIMESTAMPTZ           NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_er_status  ON emergency_routes (status);
CREATE INDEX IF NOT EXISTS idx_er_auth    ON emergency_routes (authorization_status);
CREATE INDEX IF NOT EXISTS idx_er_created ON emergency_routes (created_at DESC);

COMMENT ON TABLE emergency_routes IS 'Emergency green-wave corridor requests. Operator authorization required before activation.';


-- ── Table 7: operator_logs ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS operator_logs (
    id          SERIAL      PRIMARY KEY,
    user_id     INTEGER     REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id   INTEGER,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_log_user    ON operator_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_log_action  ON operator_logs (action);
CREATE INDEX IF NOT EXISTS idx_log_created ON operator_logs (created_at DESC);

COMMENT ON TABLE operator_logs IS 'Immutable audit trail. Every significant operator action is recorded here for accountability. Do not delete rows.';


-- ── Auto-update updated_at ─────────────────────────────────────────────────────
-- PostgreSQL does not update timestamps automatically, so we use a trigger function.

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_junctions_updated_at
    BEFORE UPDATE ON junctions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── End of schema.sql ──────────────────────────────────────────────────────────
