-- ============================================================
-- SignalAI Database Backup
-- ============================================================
-- Created: Tue Sep  1 09:54:37 IST 2026
-- Database: signalai (PostgreSQL 18.6)
-- Phase: 2/3 Database Verification
--
-- RESTORE INSTRUCTIONS:
--   1. Create database: createdb signalai
--   2. Restore: psql -d signalai -f signalai_backup.sql
--
-- WARNING: This backup contains DEMO/PROTOTYPE seed data only.
-- It does NOT contain any real passwords or credentials.
-- The password_hash values are placeholder strings.
-- ============================================================


--
-- PostgreSQL database dump
--

\restrict MC9ujH4qNq2NMgwgNE9HlwP0CCs2C0kRXVTMSzrRMsidv2fVbdBeFMYATDrq8Pe

-- Dumped from database version 18.6 (Postgres.app)
-- Dumped by pg_dump version 18.6 (Postgres.app)

-- Started on 2026-09-01 09:54:23 IST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.traffic_records DROP CONSTRAINT IF EXISTS traffic_records_junction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.signal_timings DROP CONSTRAINT IF EXISTS signal_timings_junction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.signal_timings DROP CONSTRAINT IF EXISTS signal_timings_changed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.operator_logs DROP CONSTRAINT IF EXISTS operator_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.emergency_routes DROP CONSTRAINT IF EXISTS emergency_routes_origin_junction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.emergency_routes DROP CONSTRAINT IF EXISTS emergency_routes_destination_junction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.emergency_routes DROP CONSTRAINT IF EXISTS emergency_routes_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_recommendations DROP CONSTRAINT IF EXISTS ai_recommendations_traffic_record_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_recommendations DROP CONSTRAINT IF EXISTS ai_recommendations_reviewed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_recommendations DROP CONSTRAINT IF EXISTS ai_recommendations_junction_id_fkey;
DROP TRIGGER IF EXISTS trg_users_updated_at ON public.users;
DROP TRIGGER IF EXISTS trg_junctions_updated_at ON public.junctions;
DROP INDEX IF EXISTS public.idx_users_status;
DROP INDEX IF EXISTS public.idx_users_role;
DROP INDEX IF EXISTS public.idx_users_email;
DROP INDEX IF EXISTS public.idx_traffic_recorded;
DROP INDEX IF EXISTS public.idx_traffic_level;
DROP INDEX IF EXISTS public.idx_traffic_junction;
DROP INDEX IF EXISTS public.idx_signal_junction;
DROP INDEX IF EXISTS public.idx_signal_changed;
DROP INDEX IF EXISTS public.idx_rec_status;
DROP INDEX IF EXISTS public.idx_rec_severity;
DROP INDEX IF EXISTS public.idx_rec_junction;
DROP INDEX IF EXISTS public.idx_rec_created;
DROP INDEX IF EXISTS public.idx_log_user;
DROP INDEX IF EXISTS public.idx_log_created;
DROP INDEX IF EXISTS public.idx_log_action;
DROP INDEX IF EXISTS public.idx_junctions_status;
DROP INDEX IF EXISTS public.idx_junctions_code;
DROP INDEX IF EXISTS public.idx_er_status;
DROP INDEX IF EXISTS public.idx_er_created;
DROP INDEX IF EXISTS public.idx_er_auth;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.traffic_records DROP CONSTRAINT IF EXISTS traffic_records_pkey;
ALTER TABLE IF EXISTS ONLY public.signal_timings DROP CONSTRAINT IF EXISTS signal_timings_pkey;
ALTER TABLE IF EXISTS ONLY public.operator_logs DROP CONSTRAINT IF EXISTS operator_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.junctions DROP CONSTRAINT IF EXISTS junctions_pkey;
ALTER TABLE IF EXISTS ONLY public.junctions DROP CONSTRAINT IF EXISTS junctions_junction_code_key;
ALTER TABLE IF EXISTS ONLY public.emergency_routes DROP CONSTRAINT IF EXISTS emergency_routes_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.ai_recommendations DROP CONSTRAINT IF EXISTS ai_recommendations_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.traffic_records ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.signal_timings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.operator_logs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.junctions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.emergency_routes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.ai_recommendations ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.traffic_records_id_seq;
DROP TABLE IF EXISTS public.traffic_records;
DROP SEQUENCE IF EXISTS public.signal_timings_id_seq;
DROP TABLE IF EXISTS public.signal_timings;
DROP SEQUENCE IF EXISTS public.operator_logs_id_seq;
DROP TABLE IF EXISTS public.operator_logs;
DROP SEQUENCE IF EXISTS public.junctions_id_seq;
DROP TABLE IF EXISTS public.junctions;
DROP SEQUENCE IF EXISTS public.emergency_routes_id_seq;
DROP TABLE IF EXISTS public.emergency_routes;
DROP TABLE IF EXISTS public.alembic_version;
DROP SEQUENCE IF EXISTS public.ai_recommendations_id_seq;
DROP TABLE IF EXISTS public.ai_recommendations;
DROP FUNCTION IF EXISTS public.update_updated_at_column();
DROP TYPE IF EXISTS public.user_status;
DROP TYPE IF EXISTS public.user_role;
DROP TYPE IF EXISTS public.traffic_level;
DROP TYPE IF EXISTS public.route_status;
DROP TYPE IF EXISTS public.recommendation_status;
DROP TYPE IF EXISTS public.recommendation_severity;
DROP TYPE IF EXISTS public.junction_status;
DROP TYPE IF EXISTS public.emergency_type;
DROP TYPE IF EXISTS public.authorization_status;
--
-- TOC entry 888 (class 1247 OID 16454)
-- Name: authorization_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.authorization_status AS ENUM (
    'PENDING',
    'AUTHORIZED',
    'REJECTED'
);


--
-- TOC entry 885 (class 1247 OID 16446)
-- Name: emergency_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.emergency_type AS ENUM (
    'AMBULANCE',
    'FIRE_SERVICE',
    'POLICE'
);


--
-- TOC entry 873 (class 1247 OID 16408)
-- Name: junction_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.junction_status AS ENUM (
    'NORMAL',
    'MODERATE',
    'HIGH',
    'CRITICAL'
);


--
-- TOC entry 879 (class 1247 OID 16428)
-- Name: recommendation_severity; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.recommendation_severity AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


--
-- TOC entry 882 (class 1247 OID 16438)
-- Name: recommendation_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.recommendation_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED'
);


--
-- TOC entry 891 (class 1247 OID 16462)
-- Name: route_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.route_status AS ENUM (
    'PLANNED',
    'ACTIVE',
    'COMPLETED',
    'CANCELLED'
);


--
-- TOC entry 876 (class 1247 OID 16418)
-- Name: traffic_level; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.traffic_level AS ENUM (
    'LOW',
    'MODERATE',
    'HIGH',
    'CRITICAL'
);


--
-- TOC entry 867 (class 1247 OID 16392)
-- Name: user_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_role AS ENUM (
    'TRAFFIC_OPERATOR',
    'SYSTEM_ADMINISTRATOR',
    'MUNICIPAL_AUTHORITY',
    'EMERGENCY_SERVICE'
);


--
-- TOC entry 870 (class 1247 OID 16402)
-- Name: user_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_status AS ENUM (
    'ACTIVE',
    'INACTIVE'
);


--
-- TOC entry 234 (class 1255 OID 16674)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 228 (class 1259 OID 16573)
-- Name: ai_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_recommendations (
    id integer NOT NULL,
    junction_id integer NOT NULL,
    traffic_record_id integer,
    recommendation_text text NOT NULL,
    reason text,
    current_green_time integer,
    suggested_green_time integer,
    severity public.recommendation_severity DEFAULT 'MEDIUM'::public.recommendation_severity NOT NULL,
    status public.recommendation_status DEFAULT 'PENDING'::public.recommendation_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    reviewed_at timestamp with time zone,
    reviewed_by integer,
    rejection_reason text,
    CONSTRAINT ai_recommendations_current_green_time_check CHECK ((current_green_time >= 0)),
    CONSTRAINT ai_recommendations_suggested_green_time_check CHECK ((suggested_green_time >= 0))
);


--
-- TOC entry 3987 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE ai_recommendations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.ai_recommendations IS 'AI-generated signal timing suggestions. MUST be approved by a human operator before any action is taken.';


--
-- TOC entry 3988 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN ai_recommendations.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ai_recommendations.status IS 'PENDING until an operator acts. AI never autonomously changes to APPROVED.';


--
-- TOC entry 227 (class 1259 OID 16572)
-- Name: ai_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ai_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3989 (class 0 OID 0)
-- Dependencies: 227
-- Name: ai_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ai_recommendations_id_seq OWNED BY public.ai_recommendations.id;


--
-- TOC entry 233 (class 1259 OID 16677)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- TOC entry 230 (class 1259 OID 16612)
-- Name: emergency_routes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.emergency_routes (
    id integer NOT NULL,
    emergency_type public.emergency_type NOT NULL,
    vehicle_id character varying(50) NOT NULL,
    origin_junction_id integer NOT NULL,
    destination_junction_id integer NOT NULL,
    priority integer DEFAULT 1 NOT NULL,
    route_description text,
    estimated_duration integer,
    authorization_status public.authorization_status DEFAULT 'PENDING'::public.authorization_status NOT NULL,
    status public.route_status DEFAULT 'PLANNED'::public.route_status NOT NULL,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT emergency_routes_estimated_duration_check CHECK ((estimated_duration >= 1)),
    CONSTRAINT emergency_routes_priority_check CHECK ((priority >= 1))
);


--
-- TOC entry 3990 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE emergency_routes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.emergency_routes IS 'Emergency green-wave corridor requests. Operator authorization required before activation.';


--
-- TOC entry 229 (class 1259 OID 16611)
-- Name: emergency_routes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.emergency_routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3991 (class 0 OID 0)
-- Dependencies: 229
-- Name: emergency_routes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.emergency_routes_id_seq OWNED BY public.emergency_routes.id;


--
-- TOC entry 222 (class 1259 OID 16498)
-- Name: junctions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.junctions (
    id integer NOT NULL,
    junction_code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    latitude double precision,
    longitude double precision,
    status public.junction_status DEFAULT 'NORMAL'::public.junction_status NOT NULL,
    traffic_density integer,
    current_green_time integer,
    weather_condition character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT junctions_current_green_time_check CHECK ((current_green_time >= 0)),
    CONSTRAINT junctions_traffic_density_check CHECK (((traffic_density >= 0) AND (traffic_density <= 100)))
);


--
-- TOC entry 3992 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE junctions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.junctions IS 'Monitored road intersections with traffic signals';


--
-- TOC entry 3993 (class 0 OID 0)
-- Dependencies: 222
-- Name: COLUMN junctions.junction_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.junctions.junction_code IS 'Short unique identifier, e.g. J-101';


--
-- TOC entry 3994 (class 0 OID 0)
-- Dependencies: 222
-- Name: COLUMN junctions.traffic_density; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.junctions.traffic_density IS 'Current congestion percentage (0-100)';


--
-- TOC entry 221 (class 1259 OID 16497)
-- Name: junctions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.junctions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3995 (class 0 OID 0)
-- Dependencies: 221
-- Name: junctions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.junctions_id_seq OWNED BY public.junctions.id;


--
-- TOC entry 232 (class 1259 OID 16654)
-- Name: operator_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operator_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 3996 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE operator_logs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.operator_logs IS 'Immutable audit trail. Every significant operator action is recorded here for accountability. Do not delete rows.';


--
-- TOC entry 231 (class 1259 OID 16653)
-- Name: operator_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.operator_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3997 (class 0 OID 0)
-- Dependencies: 231
-- Name: operator_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.operator_logs_id_seq OWNED BY public.operator_logs.id;


--
-- TOC entry 226 (class 1259 OID 16545)
-- Name: signal_timings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.signal_timings (
    id integer NOT NULL,
    junction_id integer NOT NULL,
    previous_green_time integer,
    new_green_time integer NOT NULL,
    reason text,
    changed_by integer,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT signal_timings_new_green_time_check CHECK ((new_green_time >= 1)),
    CONSTRAINT signal_timings_previous_green_time_check CHECK ((previous_green_time >= 0))
);


--
-- TOC entry 3998 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE signal_timings; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.signal_timings IS 'Audit trail of every signal timing change. Operator must explicitly approve before entry is created.';


--
-- TOC entry 225 (class 1259 OID 16544)
-- Name: signal_timings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.signal_timings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3999 (class 0 OID 0)
-- Dependencies: 225
-- Name: signal_timings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.signal_timings_id_seq OWNED BY public.signal_timings.id;


--
-- TOC entry 224 (class 1259 OID 16520)
-- Name: traffic_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traffic_records (
    id integer NOT NULL,
    junction_id integer NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    vehicles integer,
    traffic_level public.traffic_level DEFAULT 'LOW'::public.traffic_level NOT NULL,
    congestion_percentage integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT traffic_records_congestion_percentage_check CHECK (((congestion_percentage >= 0) AND (congestion_percentage <= 100))),
    CONSTRAINT traffic_records_vehicles_check CHECK ((vehicles >= 0))
);


--
-- TOC entry 4000 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE traffic_records; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.traffic_records IS 'Time-series traffic observations at each junction. Kaggle dataset will populate this table in Phase 3.';


--
-- TOC entry 223 (class 1259 OID 16519)
-- Name: traffic_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.traffic_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4001 (class 0 OID 0)
-- Dependencies: 223
-- Name: traffic_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.traffic_records_id_seq OWNED BY public.traffic_records.id;


--
-- TOC entry 220 (class 1259 OID 16472)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role public.user_role DEFAULT 'TRAFFIC_OPERATOR'::public.user_role NOT NULL,
    status public.user_status DEFAULT 'ACTIVE'::public.user_status NOT NULL,
    district character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_login timestamp with time zone
);


--
-- TOC entry 4002 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.users IS 'Authorized personnel who operate the SignalAI platform';


--
-- TOC entry 4003 (class 0 OID 0)
-- Dependencies: 220
-- Name: COLUMN users.password_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.password_hash IS 'Bcrypt hash — plaintext passwords are never stored';


--
-- TOC entry 4004 (class 0 OID 0)
-- Dependencies: 220
-- Name: COLUMN users.district; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.district IS 'City district this operator is assigned to';


--
-- TOC entry 219 (class 1259 OID 16471)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4005 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3747 (class 2604 OID 16576)
-- Name: ai_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_recommendations ALTER COLUMN id SET DEFAULT nextval('public.ai_recommendations_id_seq'::regclass);


--
-- TOC entry 3751 (class 2604 OID 16615)
-- Name: emergency_routes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emergency_routes ALTER COLUMN id SET DEFAULT nextval('public.emergency_routes_id_seq'::regclass);


--
-- TOC entry 3737 (class 2604 OID 16501)
-- Name: junctions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.junctions ALTER COLUMN id SET DEFAULT nextval('public.junctions_id_seq'::regclass);


--
-- TOC entry 3756 (class 2604 OID 16657)
-- Name: operator_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operator_logs ALTER COLUMN id SET DEFAULT nextval('public.operator_logs_id_seq'::regclass);


--
-- TOC entry 3745 (class 2604 OID 16548)
-- Name: signal_timings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signal_timings ALTER COLUMN id SET DEFAULT nextval('public.signal_timings_id_seq'::regclass);


--
-- TOC entry 3741 (class 2604 OID 16523)
-- Name: traffic_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traffic_records ALTER COLUMN id SET DEFAULT nextval('public.traffic_records_id_seq'::regclass);


--
-- TOC entry 3732 (class 2604 OID 16475)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3976 (class 0 OID 16573)
-- Dependencies: 228
-- Data for Name: ai_recommendations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ai_recommendations (id, junction_id, traffic_record_id, recommendation_text, reason, current_green_time, suggested_green_time, severity, status, created_at, reviewed_at, reviewed_by, rejection_reason) FROM stdin;
1	1	\N	Increase N/S green phase duration by +20 seconds to reduce Northbound queue at peak.	Traffic density at Junction J-101 is 96% — significantly above network average of 52%. Queue of ~400m on Northbound approach.	45	65	CRITICAL	PENDING	2026-08-28 12:45:28.623429+05:30	\N	\N	\N
2	2	\N	Increase E/W green phase duration by +12 seconds.	Eastbound vehicles experiencing prolonged wait times due to insufficient green time relative to current peak load.	40	52	HIGH	PENDING	2026-08-28 12:38:28.623429+05:30	\N	\N	\N
3	3	\N	Adjust signal offset by +8 seconds to synchronize with J-104 corridor.	Synchronize offset timing with adjacent Junction J-104 to create a coordinated green wave on the southbound corridor.	35	35	MEDIUM	PENDING	2026-08-28 12:23:28.623429+05:30	\N	\N	\N
6	8	\N	Temporarily increase green time by +15 seconds for 10 signal cycles.	Heavy congestion near the railway station due to train arrival. Historic patterns confirm peak load lasts approximately 15 minutes.	50	65	CRITICAL	PENDING	2026-08-28 12:01:28.623429+05:30	\N	\N	\N
4	4	\N	Increase N/S green phase by +6 seconds.	Moderate evening peak building ahead of schedule. Preventive adjustment recommended.	30	36	MEDIUM	APPROVED	2026-08-28 11:33:28.623429+05:30	2026-08-28 12:03:28.623429+05:30	1	\N
5	6	\N	Reduce cycle time by 5 seconds.	Low traffic detected. Reducing cycle time will improve overall network rhythm.	25	20	LOW	REJECTED	2026-08-28 10:58:28.623429+05:30	2026-08-28 11:28:28.623429+05:30	1	Inaccurate traffic data — sensor reading appears anomalous for this time of day.
\.


--
-- TOC entry 3981 (class 0 OID 16677)
-- Dependencies: 233
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
3a994b110de2
\.


--
-- TOC entry 3978 (class 0 OID 16612)
-- Dependencies: 230
-- Data for Name: emergency_routes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.emergency_routes (id, emergency_type, vehicle_id, origin_junction_id, destination_junction_id, priority, route_description, estimated_duration, authorization_status, status, started_at, completed_at, created_by, created_at) FROM stdin;
1	POLICE	POL-P01	2	1	1	J-102 → J-101	\N	AUTHORIZED	COMPLETED	2026-08-27 09:03:28.625831+05:30	2026-08-27 09:18:28.625831+05:30	1	2026-08-27 09:03:28.625831+05:30
2	AMBULANCE	AMB-07	1	6	1	J-101 → J-103 → J-106	\N	AUTHORIZED	COMPLETED	2026-08-28 11:17:28.625831+05:30	2026-08-28 11:33:28.625831+05:30	1	2026-08-28 11:17:28.625831+05:30
3	FIRE_SERVICE	FIRE-E12	4	8	1	J-104 → J-108	\N	AUTHORIZED	COMPLETED	2026-08-27 08:03:28.625831+05:30	2026-08-27 08:23:28.625831+05:30	1	2026-08-27 08:03:28.625831+05:30
\.


--
-- TOC entry 3970 (class 0 OID 16498)
-- Dependencies: 222
-- Data for Name: junctions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.junctions (id, junction_code, name, latitude, longitude, status, traffic_density, current_green_time, weather_condition, created_at, updated_at) FROM stdin;
1	J-101	Main St & 5th Ave	28.65	77.21	HIGH	96	45	Light Rain, 27°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
2	J-102	Broadway & 8th	28.64	77.22	HIGH	88	40	Clear, 29°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
3	J-103	Park Ave & Central	28.66	77.2	MODERATE	62	35	Cloudy, 28°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
4	J-104	Oak St & 2nd Ave	28.63	77.23	MODERATE	55	30	Clear, 30°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
5	J-105	Elm Rd & North Ring	28.67	77.19	NORMAL	28	30	Clear, 30°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
6	J-106	Lake View & Sector 3	28.62	77.24	NORMAL	18	25	Clear, 30°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
7	J-107	Industrial Bypass	28.68	77.18	NORMAL	12	25	Clear, 29°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
8	J-108	Station Rd & MG Ave	28.61	77.25	HIGH	92	50	Humid, 31°C	2026-08-28 13:03:28.618785+05:30	2026-08-28 13:03:28.618785+05:30
\.


--
-- TOC entry 3980 (class 0 OID 16654)
-- Dependencies: 232
-- Data for Name: operator_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.operator_logs (id, user_id, action, entity_type, entity_id, description, created_at) FROM stdin;
1	1	SUBMIT_RECOMMENDATION	ai_recommendation	\N	Recommendation AI-9042 submitted for J-101	2026-08-28 12:45:28.62742+05:30
2	1	APPROVE_RECOMMENDATION	ai_recommendation	\N	Operator approved recommendation AI-9036 for J-104	2026-08-28 12:38:28.62742+05:30
3	1	ACTIVATE_EMERGENCY_ROUTE	emergency_route	\N	Emergency Route ER-041 authorized — Ambulance AMB-07	2026-08-28 12:18:28.62742+05:30
4	1	SENSOR_ALERT	junction	\N	Sensor offline alert: J-107 (resolved)	2026-08-28 12:01:28.62742+05:30
5	1	APPROVE_RECOMMENDATION	ai_recommendation	\N	Recommendation AI-9035 applied to J-104	2026-08-28 11:33:28.62742+05:30
\.


--
-- TOC entry 3974 (class 0 OID 16545)
-- Dependencies: 226
-- Data for Name: signal_timings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.signal_timings (id, junction_id, previous_green_time, new_green_time, reason, changed_by, changed_at) FROM stdin;
1	4	30	36	Preventive adjustment: Moderate evening peak building ahead of schedule. Recommendation AI-9035 applied.	1	2026-08-28 12:03:28.622114+05:30
\.


--
-- TOC entry 3972 (class 0 OID 16520)
-- Dependencies: 224
-- Data for Name: traffic_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.traffic_records (id, junction_id, recorded_at, vehicles, traffic_level, congestion_percentage, created_at) FROM stdin;
1	1	2026-08-28 12:53:28.620093+05:30	184	CRITICAL	96	2026-08-28 13:03:28.620093+05:30
2	2	2026-08-28 12:53:28.620093+05:30	162	HIGH	88	2026-08-28 13:03:28.620093+05:30
3	3	2026-08-28 12:53:28.620093+05:30	98	MODERATE	62	2026-08-28 13:03:28.620093+05:30
4	4	2026-08-28 12:53:28.620093+05:30	87	MODERATE	55	2026-08-28 13:03:28.620093+05:30
5	5	2026-08-28 12:53:28.620093+05:30	42	LOW	28	2026-08-28 13:03:28.620093+05:30
6	6	2026-08-28 12:53:28.620093+05:30	26	LOW	18	2026-08-28 13:03:28.620093+05:30
7	7	2026-08-28 12:53:28.620093+05:30	19	LOW	12	2026-08-28 13:03:28.620093+05:30
8	8	2026-08-28 12:53:28.620093+05:30	175	CRITICAL	92	2026-08-28 13:03:28.620093+05:30
\.


--
-- TOC entry 3968 (class 0 OID 16472)
-- Dependencies: 220
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, name, email, password_hash, role, status, district, created_at, updated_at, last_login) FROM stdin;
1	J. Sharma	j.sharma@signalai.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	TRAFFIC_OPERATOR	ACTIVE	North	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
2	R. Mehta	r.mehta@signalai.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	SYSTEM_ADMINISTRATOR	ACTIVE	\N	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
3	P. Verma	p.verma@signalai.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	TRAFFIC_OPERATOR	ACTIVE	South	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
4	S. Gupta	s.gupta@municipal.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	MUNICIPAL_AUTHORITY	ACTIVE	\N	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
5	A. Khan	a.khan@emergency.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	EMERGENCY_SERVICE	ACTIVE	North	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
6	K. Singh	k.singh@signalai.gov.in	$2b$12$PLACEHOLDER_HASH_PHASE1_DEMO_ONLY_NOT_REAL	TRAFFIC_OPERATOR	INACTIVE	East	2026-08-28 13:03:28.616699+05:30	2026-08-28 13:03:28.616699+05:30	\N
\.


--
-- TOC entry 4006 (class 0 OID 0)
-- Dependencies: 227
-- Name: ai_recommendations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ai_recommendations_id_seq', 6, true);


--
-- TOC entry 4007 (class 0 OID 0)
-- Dependencies: 229
-- Name: emergency_routes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.emergency_routes_id_seq', 3, true);


--
-- TOC entry 4008 (class 0 OID 0)
-- Dependencies: 221
-- Name: junctions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.junctions_id_seq', 9, true);


--
-- TOC entry 4009 (class 0 OID 0)
-- Dependencies: 231
-- Name: operator_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.operator_logs_id_seq', 5, true);


--
-- TOC entry 4010 (class 0 OID 0)
-- Dependencies: 225
-- Name: signal_timings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.signal_timings_id_seq', 1, true);


--
-- TOC entry 4011 (class 0 OID 0)
-- Dependencies: 223
-- Name: traffic_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.traffic_records_id_seq', 9, true);


--
-- TOC entry 4012 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- TOC entry 3791 (class 2606 OID 16591)
-- Name: ai_recommendations ai_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_pkey PRIMARY KEY (id);


--
-- TOC entry 3807 (class 2606 OID 16682)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3797 (class 2606 OID 16634)
-- Name: emergency_routes emergency_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emergency_routes
    ADD CONSTRAINT emergency_routes_pkey PRIMARY KEY (id);


--
-- TOC entry 3778 (class 2606 OID 16516)
-- Name: junctions junctions_junction_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.junctions
    ADD CONSTRAINT junctions_junction_code_key UNIQUE (junction_code);


--
-- TOC entry 3780 (class 2606 OID 16514)
-- Name: junctions junctions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.junctions
    ADD CONSTRAINT junctions_pkey PRIMARY KEY (id);


--
-- TOC entry 3805 (class 2606 OID 16665)
-- Name: operator_logs operator_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operator_logs
    ADD CONSTRAINT operator_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3789 (class 2606 OID 16559)
-- Name: signal_timings signal_timings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signal_timings
    ADD CONSTRAINT signal_timings_pkey PRIMARY KEY (id);


--
-- TOC entry 3785 (class 2606 OID 16535)
-- Name: traffic_records traffic_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traffic_records
    ADD CONSTRAINT traffic_records_pkey PRIMARY KEY (id);


--
-- TOC entry 3772 (class 2606 OID 16493)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 3774 (class 2606 OID 16491)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3798 (class 1259 OID 16651)
-- Name: idx_er_auth; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_er_auth ON public.emergency_routes USING btree (authorization_status);


--
-- TOC entry 3799 (class 1259 OID 16652)
-- Name: idx_er_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_er_created ON public.emergency_routes USING btree (created_at DESC);


--
-- TOC entry 3800 (class 1259 OID 16650)
-- Name: idx_er_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_er_status ON public.emergency_routes USING btree (status);


--
-- TOC entry 3775 (class 1259 OID 16517)
-- Name: idx_junctions_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_junctions_code ON public.junctions USING btree (junction_code);


--
-- TOC entry 3776 (class 1259 OID 16518)
-- Name: idx_junctions_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_junctions_status ON public.junctions USING btree (status);


--
-- TOC entry 3801 (class 1259 OID 16672)
-- Name: idx_log_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_log_action ON public.operator_logs USING btree (action);


--
-- TOC entry 3802 (class 1259 OID 16673)
-- Name: idx_log_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_log_created ON public.operator_logs USING btree (created_at DESC);


--
-- TOC entry 3803 (class 1259 OID 16671)
-- Name: idx_log_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_log_user ON public.operator_logs USING btree (user_id);


--
-- TOC entry 3792 (class 1259 OID 16610)
-- Name: idx_rec_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rec_created ON public.ai_recommendations USING btree (created_at DESC);


--
-- TOC entry 3793 (class 1259 OID 16607)
-- Name: idx_rec_junction; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rec_junction ON public.ai_recommendations USING btree (junction_id);


--
-- TOC entry 3794 (class 1259 OID 16609)
-- Name: idx_rec_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rec_severity ON public.ai_recommendations USING btree (severity);


--
-- TOC entry 3795 (class 1259 OID 16608)
-- Name: idx_rec_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rec_status ON public.ai_recommendations USING btree (status);


--
-- TOC entry 3786 (class 1259 OID 16571)
-- Name: idx_signal_changed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_signal_changed ON public.signal_timings USING btree (changed_at DESC);


--
-- TOC entry 3787 (class 1259 OID 16570)
-- Name: idx_signal_junction; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_signal_junction ON public.signal_timings USING btree (junction_id);


--
-- TOC entry 3781 (class 1259 OID 16541)
-- Name: idx_traffic_junction; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traffic_junction ON public.traffic_records USING btree (junction_id);


--
-- TOC entry 3782 (class 1259 OID 16543)
-- Name: idx_traffic_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traffic_level ON public.traffic_records USING btree (traffic_level);


--
-- TOC entry 3783 (class 1259 OID 16542)
-- Name: idx_traffic_recorded; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traffic_recorded ON public.traffic_records USING btree (recorded_at DESC);


--
-- TOC entry 3768 (class 1259 OID 16494)
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- TOC entry 3769 (class 1259 OID 16495)
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- TOC entry 3770 (class 1259 OID 16496)
-- Name: idx_users_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_status ON public.users USING btree (status);


--
-- TOC entry 3819 (class 2620 OID 16676)
-- Name: junctions trg_junctions_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_junctions_updated_at BEFORE UPDATE ON public.junctions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3818 (class 2620 OID 16675)
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3811 (class 2606 OID 16592)
-- Name: ai_recommendations ai_recommendations_junction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_junction_id_fkey FOREIGN KEY (junction_id) REFERENCES public.junctions(id) ON DELETE CASCADE;


--
-- TOC entry 3812 (class 2606 OID 16602)
-- Name: ai_recommendations ai_recommendations_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3813 (class 2606 OID 16597)
-- Name: ai_recommendations ai_recommendations_traffic_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_traffic_record_id_fkey FOREIGN KEY (traffic_record_id) REFERENCES public.traffic_records(id) ON DELETE SET NULL;


--
-- TOC entry 3814 (class 2606 OID 16645)
-- Name: emergency_routes emergency_routes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emergency_routes
    ADD CONSTRAINT emergency_routes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3815 (class 2606 OID 16640)
-- Name: emergency_routes emergency_routes_destination_junction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emergency_routes
    ADD CONSTRAINT emergency_routes_destination_junction_id_fkey FOREIGN KEY (destination_junction_id) REFERENCES public.junctions(id) ON DELETE RESTRICT;


--
-- TOC entry 3816 (class 2606 OID 16635)
-- Name: emergency_routes emergency_routes_origin_junction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.emergency_routes
    ADD CONSTRAINT emergency_routes_origin_junction_id_fkey FOREIGN KEY (origin_junction_id) REFERENCES public.junctions(id) ON DELETE RESTRICT;


--
-- TOC entry 3817 (class 2606 OID 16666)
-- Name: operator_logs operator_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operator_logs
    ADD CONSTRAINT operator_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3809 (class 2606 OID 16565)
-- Name: signal_timings signal_timings_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signal_timings
    ADD CONSTRAINT signal_timings_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3810 (class 2606 OID 16560)
-- Name: signal_timings signal_timings_junction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signal_timings
    ADD CONSTRAINT signal_timings_junction_id_fkey FOREIGN KEY (junction_id) REFERENCES public.junctions(id) ON DELETE CASCADE;


--
-- TOC entry 3808 (class 2606 OID 16536)
-- Name: traffic_records traffic_records_junction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traffic_records
    ADD CONSTRAINT traffic_records_junction_id_fkey FOREIGN KEY (junction_id) REFERENCES public.junctions(id) ON DELETE CASCADE;


-- Completed on 2026-09-01 09:54:23 IST

--
-- PostgreSQL database dump complete
--

\unrestrict MC9ujH4qNq2NMgwgNE9HlwP0CCs2C0kRXVTMSzrRMsidv2fVbdBeFMYATDrq8Pe

