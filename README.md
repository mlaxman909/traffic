# 🚦 SignalAI — Municipal Traffic Control Portal

> **BCA Mini Project — Full Stack Smart Traffic Signal Optimization Platform**  
> An AI-driven traffic management system for urban intersections in Vadodara, India.

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [📸 Screenshots](#2--screenshots)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Installation Guide](#5-installation-guide)
6. [🔐 Login Credentials](#6--login-credentials)
7. [User Roles & Accounts](#7-user-roles--accounts)
8. [Application Pages & Process Flow](#8-application-pages--process-flow)
9. [Navigation & Routing](#9-navigation--routing)
10. [Design System](#10-design-system)
11. [JWT Authentication](#11-jwt-authentication)
12. [AI Recommendation Engine](#12-ai-recommendation-engine)
13. [TomTom Map Integration](#13-tomtom-map-integration)
14. [Vadodara Road Network (OSM)](#14-vadodara-road-network-osm)
15. [Database Schema & Status](#15-database-schema--status)
16. [API Endpoints & CRUD](#16-api-endpoints--crud)
17. [Testing & Verification](#17-testing--verification)
18. [Development Phases](#18-development-phases)
19. [Performance Report](#19-performance-report)
20. [Project Status](#20-project-status)
21. [Faculty Demo Guide](#21-faculty-demo-guide)
22. [Scripts](#22-scripts)
23. [Future Scope & Limitations](#23-future-scope--limitations)

---

## 1. Project Overview

**SignalAI** is an advanced, AI-driven traffic management system designed for municipal traffic control centers. It provides operators and administrators with a centralized, intuitive interface to:

- 📍 Monitor intersections in real time with a live TomTom map
- 📊 Analyze traffic flow with charts and analytics (real PostgreSQL data)
- 🤖 Review and approve/reject AI-generated signal optimization recommendations
- 🚨 Activate emergency routing (Green Wave) for ambulances, fire trucks, and police
- 💬 Query the AI assistant for traffic insights
- 👥 Manage operator accounts and access levels (admin only)
- 🗺️ Visualize Vadodara road network via OpenStreetMap (45,903 road segments)

> **Note:** SignalAI does **NOT** control real traffic signals — it is a decision-support prototype. All traffic data comes from 23,048 real Vadodara traffic records in PostgreSQL.

---

## 2. 📸 Screenshots

> Real screenshots captured from the live application with PostgreSQL backend connected.

### 🔐 Login Page
![Login Page](public/screenshots/login.png)

---

### 📊 Dashboard — Overview & KPIs
![Dashboard](public/screenshots/dashboard.png)

---

### 🗺️ Traffic Map — Live Junction Monitor
![Traffic Map](public/screenshots/traffic_map.png)

---

### 📈 Analytics & Reporting
![Analytics](public/screenshots/analytics.png)

---

### 🤖 Decision Queue — AI Recommendations
![Decision Queue](public/screenshots/decision_queue.png)

---

### 🚨 Emergency Routing — Green Wave
![Emergency Routing](public/screenshots/emergency_routing.png)

---

### 💬 SignalAI Assistant
![SignalAI Assistant](public/screenshots/assistant.png)

---

### ⚙️ Settings
![Settings](public/screenshots/settings.png)

---

### 👥 Admin — User Management
![Admin Users](public/screenshots/admin_users.png)

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 18 (via Vite 8) |
| **Routing** | React Router DOM v7 |
| **Styling** | CSS Modules (locally scoped per component) |
| **Charts / Visualizations** | Recharts v3 |
| **Icons** | Lucide React v1 |
| **Linter** | OxLint |
| **Build Tool** | Vite 8 |
| **Markup** | Semantic HTML5 + JSX |
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL 16+ |
| **ORM** | SQLAlchemy + Alembic (migrations) |
| **Auth** | JWT (PyJWT + Argon2 password hashing) |
| **Map Provider** | TomTom Maps API v1 (MapLibre GL via CDN) |
| **Road Data** | OpenStreetMap (ODbL License) |

---

## 4. Project Structure

```
traffic/
├── index.html                          # App entry point (HTML shell + MapLibre CDN)
├── vite.config.js                      # Vite build configuration + API proxy
├── package.json                        # Dependencies and scripts
├── .oxlintrc.json                      # Linting rules
├── .env                                # Environment variables (TomTom key, DB URL)
├── start.sh                            # Start all services
├── stop.sh                             # Stop all services
│
├── src/
│   ├── main.jsx                        # React DOM entry point
│   ├── App.jsx                         # Root router + protected routes
│   ├── global.css                      # Global CSS resets and base styles
│   │
│   ├── contexts/
│   │   └── AuthContext.jsx             # JWT auth state (currentUser, token, login, logout)
│   │
│   ├── components/
│   │   ├── Navigation/
│   │   │   ├── Sidebar.jsx             # Left navigation sidebar
│   │   │   └── Header.jsx              # Top bar (notifications, user profile)
│   │   ├── Shared/
│   │   │   ├── Button.jsx              # Reusable button component
│   │   │   └── FormInput.jsx           # Reusable form input component
│   │   └── ProtectedRoute.jsx          # JWT route guard (role-based)
│   │
│   ├── pages/
│   │   ├── Login.jsx                   # JWT authentication screen
│   │   ├── Dashboard.jsx               # KPI overview & real PostgreSQL data
│   │   ├── TrafficMap.jsx              # TomTom map + OSM roads + junction markers
│   │   ├── Analytics.jsx               # Charts, trends, & comparisons
│   │   ├── DecisionQueue.jsx           # AI recommendations queue (approve/reject)
│   │   ├── EmergencyRouting.jsx        # Green wave / emergency routing
│   │   ├── Assistant.jsx               # AI chatbot interface (prototype)
│   │   ├── Settings.jsx                # User preferences & profile
│   │   └── AdminUsers.jsx              # User management (Admin only)
│   │
│   └── services/
│       └── api.js                      # Axios instance with JWT interceptor
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app entry point
│   │   ├── database.py                 # SQLAlchemy session + engine
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── routers/                    # FastAPI route handlers (one per entity)
│   │   └── services/
│   │       ├── auth.py                 # JWT + Argon2 password verification
│   │       └── recommendation_engine.py # Rule-based AI engine
│   ├── alembic/                        # Database migrations
│   ├── import_vadodara_roads.py        # OSM road network import script
│   ├── test_api.py                     # API test suite
│   ├── test_business_logic.py          # Business logic tests
│   └── test_ai_engine.py              # AI engine tests
│
├── database/
│   ├── schema.sql                      # Database DDL (8 tables)
│   └── seed.sql                        # Demo seed data
│
└── data/
    └── vadodara_road_network.geojson   # OSM road data (~35 MB)
```

---

## 5. Installation Guide

### Prerequisites

| Software | Version Required |
|---|---|
| Node.js | 18+ |
| npm | 9+ |
| Python | 3.11+ |
| PostgreSQL | 16+ |

> **Platform:** macOS (Postgres.app recommended). For Windows, use the PostgreSQL installer from postgresql.org.

---

### Step 1 — Install PostgreSQL

**macOS (recommended):**
1. Download from: https://postgresapp.com/
2. Move to `/Applications` and click **Initialize**
3. Add to PATH:
```bash
echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify:
```bash
psql --version
pg_isready
```

---

### Step 2 — Create the Database

```bash
createdb signalai
```

---

### Step 3 — Apply Database Schema

From the project root:

```bash
psql -d signalai -f database/schema.sql
```

Expected: 7 `CREATE TABLE` messages + indexes + triggers.

Verify:
```bash
psql -d signalai -c "\dt"
```

Expected tables: `ai_recommendations`, `emergency_routes`, `junctions`, `operator_logs`, `signal_timings`, `traffic_records`, `users`

---

### Step 4 — Load Seed Data

```bash
psql -d signalai -f database/seed.sql
```

Expected output:
```
 users              |  6
 junctions          |  8
 traffic_records    |  8
 signal_timings     |  1
 ai_recommendations |  6
 emergency_routes   |  3
 operator_logs      |  5
```

---

### Step 5 — Set Up Python Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

---

### Step 6 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

Installs: FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic, Alembic, python-dotenv, PyJWT, pwdlib[argon2], python-multipart.

---

### Step 7 — Configure .env

Edit `.env` in the project root:

```env
DATABASE_URL=postgresql://YOUR_MACOS_USERNAME@localhost:5432/signalai
VITE_TOMTOM_API_KEY=<your-tomtom-api-key>
APP_ENV=development
FRONTEND_URL=http://localhost:5173
```

> **No password needed** for Postgres.app local connections.  
> Get your username: `whoami`

---

### Step 8 — Configure Alembic (Migration Tracking)

If tables already created via schema.sql:

```bash
cd backend
source venv/bin/activate
alembic stamp head
```

For future schema changes:
```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

---

### Step 9 — Start the FastAPI Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Expected:
```
  SignalAI API v1.0.0 starting up
  Swagger UI  : http://localhost:8000/docs
  Health check: http://localhost:8000/api/health
```

---

### Step 10 — Install Frontend & Start

Open a **new terminal**:

```bash
npm install
npm run dev
```

Open: **http://localhost:5173**

---

### Step 11 — Verify Full Stack

| Check | URL | Expected |
|---|---|---|
| React frontend | http://localhost:5173 | SignalAI login page |
| API health | http://localhost:8000/api/health | `{"status":"ok"}` |
| DB connected | http://localhost:8000/api/health/database | `{"status":"ok","database":"connected"}` |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |
| List users | http://localhost:8000/api/users | JSON array of 6 users |
| List junctions | http://localhost:8000/api/junctions | JSON array of 8 junctions |

---

### Quick Start (Single Command)

```bash
bash start.sh
```

Stop all services:
```bash
bash stop.sh
```

---

### Troubleshooting

**"psql: command not found"**
```bash
echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**"database 'signalai' does not exist"**
```bash
createdb signalai && psql -d signalai -f database/schema.sql && psql -d signalai -f database/seed.sql
```

**"FastAPI shows database: disconnected"**
- Check Postgres.app is running (green indicator in menu bar)
- Check `.env` has correct `DATABASE_URL` with your macOS username (`whoami`)

**"FATAL: role 'postgres' does not exist"**  
Postgres.app uses your macOS username, not `postgres`. Update `DATABASE_URL` in `.env`.

**"connection refused" on port 5432**  
Postgres.app is not running. Open from Applications and click Initialize/Start.

---

### Database Backup & Restore

```bash
# Create backup
pg_dump -d signalai --no-owner --no-privileges -f database/signalai_backup.sql

# Restore
createdb signalai_restored
psql -d signalai_restored -f database/signalai_backup.sql
```

---

## 6. 🔐 Login Credentials

### Demo Credentials (Full Access)

| Role | Email | Password |
|------|-------|----------|
| Traffic Operator | j.sharma@signalai.gov.in | password123 |
| System Administrator | r.mehta@signalai.gov.in | password123 |
| Municipal Authority | s.gupta@municipal.gov.in | password123 |
| Emergency Service | a.khan@emergency.gov.in | password123 |

> All passwords are hashed with **Argon2** in the database. No plaintext passwords are stored.

### How Login Works

1. User enters **Email Address** and **Password** on the Login page
2. Frontend sends `POST /api/auth/login` (form-encoded)
3. Backend validates credentials via Argon2 hash comparison
4. On success → JWT access token returned → stored in `localStorage`
5. All subsequent API requests include `Authorization: Bearer <token>` header
6. All other routes are **protected** — unauthenticated users are redirected to `/login`
7. To log out: JWT is cleared from `localStorage`

---

## 7. User Roles & Accounts

### 👤 System Users Table

| ID | Name | Email | Role | District | Status |
|---|---|---|---|---|---|
| `OP-4092` | J. Sharma | j.sharma@signalai.gov.in | Traffic Operator | North | 🟢 Active |
| `AD-1001` | R. Mehta | r.mehta@signalai.gov.in | **System Administrator** | All | 🟢 Active |
| `OP-4091` | P. Verma | p.verma@signalai.gov.in | Traffic Operator | South | 🟢 Active |
| `MA-2001` | S. Gupta | s.gupta@municipal.gov.in | Municipal Authority | All | 🟢 Active |
| `ES-3001` | A. Khan | a.khan@emergency.gov.in | Emergency Service | North | 🟢 Active |
| `OP-4090` | K. Singh | k.singh@signalai.gov.in | Traffic Operator | East | 🔴 Disabled |

### 🔑 Role Descriptions

| Role | Access Level | Primary Responsibilities |
|---|---|---|
| **System Administrator** | Full access | Manage users, system settings, AI parameters, all modules |
| **Traffic Operator** | Standard | Monitor junctions, approve/reject AI recommendations, view maps |
| **Municipal Authority** | Read + Reports | View analytics, dashboard overviews, generate reports |
| **Emergency Service** | Emergency module | Activate green wave routing, view emergency history |

---

## 8. Application Pages & Process Flow

### 🔄 Overall User Flow

```
[Browser] → /login
              │
              ▼ (JWT login)
           /dashboard ──────────────────────────────────────────┐
              │                                                  │
     ┌────────┼────────────────────────────────────────┐        │
     ▼        ▼        ▼        ▼        ▼        ▼    ▼        │
  /traffic  /analytics /decision /emergency /assistant /settings │
  -map               -queue    -routing               /admin/users
```

---

### Page-by-Page Process

#### 1. 🔐 Login (`/login`)
**Purpose:** Secure JWT entry point for all authorized personnel.

**Process:**
1. User enters **Email Address** and **Password**
2. Frontend calls `POST /api/auth/login`
3. On success → JWT stored in localStorage → redirects to `/dashboard`
4. On failure → error banner: *"Authentication failed. Verify credentials."*

---

#### 2. 📊 Dashboard (`/dashboard`)
**Purpose:** High-level summary of the entire traffic network at a glance.

**Data Sources:** 4 parallel PostgreSQL API calls via `Promise.all`:
- `GET /api/junctions` — 8 junction records
- `GET /api/traffic-records/summary` — Aggregated stats
- `GET /api/ai-recommendations?status=PENDING` — Pending AI recommendations
- `GET /api/operator-logs?limit=5` — 5 recent operator actions

**KPI Data:**

| Metric | Value |
|---|---|
| Total Junctions | 8 |
| Active Signals | 8 |
| Congested Junctions | 3 (density > 80%) |
| Pending AI Recommendations | varies |
| Active Emergency Routes | varies |

---

#### 3. 🗺️ Traffic Map (`/traffic-map`)
**Purpose:** Visualize all intersections and their current congestion levels on a TomTom map.

**Process:**
1. TomTom basemap loads centered on Vadodara
2. 8 junction markers appear at precise GPS coordinates
3. Clicking a junction marker → detail panel opens
4. OSM road network overlay renders behind markers

**Status Color Codes:**
- 🔴 **Red** — Critical congestion (density > 80%)
- 🟡 **Yellow** — Moderate congestion (density 50–80%)
- 🟢 **Green** — Clear (density < 50%)

**Mock Junctions (Vadodara GPS):**

| Code | Location | Status | Density | Latitude | Longitude |
|---|---|---|---|---|---|
| J-101 | Genda Circle | 🔴 Red | 96% | 22.3056 | 73.1764 |
| J-102 | Kala Ghoda Circle | 🔴 Red | 88% | 22.3054 | 73.1818 |
| J-108 | Akota Circle | 🔴 Red | 92% | 22.2933 | 73.1721 |
| J-103 | Chakli Circle | 🟡 Yellow | 62% | 22.3086 | 73.1650 |
| J-104 | Fatehgunj Circle | 🟡 Yellow | 55% | 22.3207 | 73.1882 |
| J-105 | Amit Nagar Circle | 🟢 Green | 28% | 22.3168 | 73.1975 |
| J-106 | Susen Circle | 🟢 Green | 18% | 22.2994 | 73.2081 |
| J-107 | Muktanand Circle | 🟢 Green | 12% | 22.3218 | 73.1979 |

---

#### 4. 📈 Analytics (`/analytics`)
**Purpose:** Historical data trends and predictive traffic pattern visualizations.

**Charts Available:**
- **Congestion Trend (Line Chart):** 24-hour congestion % vs. historical baseline
- **Peak Hour Volume (Bar Chart):** Hourly vehicle volume from 06:00–21:00
- **Vehicle Movement (Area Chart):** Demo prototype data — clearly labelled
- **Junction Comparison (Table):** Top 5 junctions ranked by density

---

#### 5. 🤖 Decision Queue (`/decision-queue`)
**Purpose:** AI-generated signal optimization recommendations awaiting operator review.

**Process:**
1. Queue loads pending AI recommendations (from PostgreSQL)
2. Operator clicks **Run AI Engine** → Rule-based engine generates new recommendations
3. Operator clicks **✅ Approve** → status = `APPROVED`, operator log created
4. Operator clicks **❌ Reject** → enters reason → status = `REJECTED`, operator log created
5. All `reviewed_by` values are set from authenticated JWT user ID

---

#### 6. 🚨 Emergency Routing (`/emergency-routing`)
**Purpose:** Rapidly clear a traffic path (Green Wave) for emergency response vehicles.

**Process:**
1. Select **Emergency Type** (Ambulance / Fire Service / Police)
2. Enter **Origin Junction** and **Destination Junction**
3. Click **"Initiate Green Wave"** → route stored in PostgreSQL
4. Route status can be activated, completed, or cancelled

---

#### 7. 💬 SignalAI Assistant (`/assistant`)
**Purpose:** Conversational AI interface for querying system status. *(Prototype — uses static mock responses)*

---

#### 8. ⚙️ Settings (`/settings`)
**Purpose:** Shows currently authenticated user's profile. Password change form (UI only).

---

#### 9. 👥 Admin — User Management (`/admin/users`)
**Purpose:** System administrators manage operator accounts and role assignments.

**Access:** Only `SYSTEM_ADMINISTRATOR` role. Non-admins receive **403 Forbidden**.

**Operations:** Create, Read, Update, Delete users. New users set to `INACTIVE` by default.

---

## 9. Navigation & Routing

| Route | Page | Auth Required |
|---|---|---|
| `/login` | Login Screen | ❌ Public |
| `/dashboard` | Dashboard | ✅ Protected |
| `/traffic-map` | Traffic Map | ✅ Protected |
| `/analytics` | Analytics | ✅ Protected |
| `/decision-queue` | Decision Queue | ✅ Protected |
| `/emergency-routing` | Emergency Routing | ✅ Protected |
| `/assistant` | SignalAI Assistant | ✅ Protected |
| `/settings` | Settings | ✅ Protected |
| `/admin/users` | Admin User Management | ✅ Protected (Admin only) |
| `*` (any unknown) | → Redirects to `/login` | — |

### Authentication Guard

The `ProtectedRoute` component guards all protected routes:
- Checks JWT token validity via `/api/auth/me`
- If not authenticated → redirects to `/login`
- Supports role-based protection: `allowedRoles={['SYSTEM_ADMINISTRATOR']}`

---

## 10. Design System

### Color Palette (Dark Theme)

| Token | Color | Usage |
|---|---|---|
| Background | `#0a0f1a` | Main app background |
| Surface | `#111827` | Cards and panels |
| Border | `#1f2937` | Dividers and outlines |
| Accent Green | `#22c55e` | Success, optimal flow, logo |
| Accent Yellow | `#f59e0b` | Warnings, moderate congestion |
| Accent Red | `#ef4444` | Critical alerts, errors, emergencies |
| Accent Blue | `#3b82f6` | Information, AI indicators |
| Text Primary | `#f9fafb` | Main text |
| Text Secondary | `#9ca3af` | Labels and subtitles |

### Typography
- **Font:** Inter / Roboto (Sans-serif)
- **Sizing:** Fluid scale from 12px (labels) to 28px (headings)

### Design Goals
- **Clarity:** High-contrast visualization for traffic data — minimizes operator cognitive load
- **Intuitiveness:** Critical alerts and emergency tools immediately accessible
- **Scalability:** Modular, reusable UI components (CSS Modules, no class conflicts)
- **Responsiveness:** Maintains integrity across control center monitor resolutions

---

## 11. JWT Authentication

### Backend (FastAPI)

**Dependencies:** `pwdlib[argon2]`, `PyJWT`, `python-multipart`

**Endpoints:**
- `POST /api/auth/login` — Accepts `username` (email) + `password` as `x-www-form-urlencoded`. Returns JWT.
- `GET /api/auth/me` — Returns current user details from token (no password hash exposed)

**Security:**
- All 6 demo users have Argon2-hashed passwords (`"password123"`)
- `get_current_user` dependency applied to **ALL** write operations (POST, PUT, DELETE)
- `reviewed_by`, `created_by`, `user_id` in all records sourced from `current_user.id` — never hardcoded
- Auto global logout on `401 Unauthorized`

### Frontend (React)

- **`AuthContext.jsx`**: Global auth state (currentUser, token, isAuthenticated, login, logout)
- **`ProtectedRoute.jsx`**: Guards routes, redirects unauthenticated users to `/login`
- **`api.js`**: Axios interceptor prepends `Authorization: Bearer <token>` to all requests

---

## 12. AI Recommendation Engine

### Architecture

The AI engine is a **transparent, rule-based system** (NOT machine learning). It analyzes real traffic data from `traffic_records` and applies threshold rules.

**Endpoint:** `POST /api/ai-recommendations/generate`

**Rules:**

| Condition | Severity | Action |
|---|---|---|
| Congestion ≥ 80% | **CRITICAL** | Increase green time +20s (max 120s) |
| Congestion ≥ 60% | **HIGH** | Increase green time +10s |
| Congestion ≤ 20% | **LOW** | Decrease green time -10s (min 20s) |

**Duplicate Prevention:** Skips junctions already with a `PENDING` recommendation of the same severity — prevents operator fatigue.

**Human-readable explanations** include time-of-day context (morning peak, evening peak, off-peak).

### Workflow

```
traffic_records (PostgreSQL)
        ↓
Rule-Based Engine evaluates thresholds
        ↓
ai_recommendations table (PostgreSQL)
        ↓
Decision Queue (frontend) — operator approves/rejects
        ↓
operator_logs (immutable audit trail)
```

---

## 13. TomTom Map Integration

**Provider:** TomTom Maps API v1  
**Renderer:** MapLibre GL JS (loaded via CDN — avoids Vite bundler conflicts with WebWorkers)  
**Tile URL:** `https://api.tomtom.com/map/1/tile/basic/main/{z}/{x}/{y}.png`  
**API Key:** `VITE_TOMTOM_API_KEY` in `.env` — never hardcoded in source

### Architecture

```
Browser
  └─ index.html
       └─ <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js">
  └─ TrafficMap.jsx
       └─ window.maplibregl (CDN global)
            └─ new Map({ style: getTomTomStyle(VITE_TOMTOM_API_KEY) })
                  └─ TomTom raster tiles
```

### Features

| Feature | Status |
|---------|--------|
| Raster tile map (TomTom basemap) | ✅ Working |
| Centred on Vadodara (22.3076°N, 73.1866°E) | ✅ |
| Zoom level 13 (street level) | ✅ |
| Navigation controls (zoom +/-) | ✅ |
| 8 Junction markers (real DB coordinates) | ✅ |
| Color coding by traffic status | ✅ |
| Hover popup with junction name | ✅ |
| Click to open detail panel | ✅ |
| Search filter | ✅ |
| Status filter (All/Congested/Moderate/Low) | ✅ |
| OSM road network overlay | ✅ |

### Data Sources

| Data | Source |
|------|--------|
| Map tiles / basemap | TomTom Maps API |
| Junction locations (lat/lng) | SignalAI PostgreSQL database |
| Traffic density / status | SignalAI PostgreSQL database |
| Road network overlay | OpenStreetMap (45,903 road records) |

**API Key Verified:** HTTP 200 confirmed on `api.tomtom.com/map/1/tile/...` (22 Sept 2026)

---

## 14. Vadodara Road Network (OSM)

**Source:** OpenStreetMap contributors  
**License:** Open Database License (ODbL)  
**Attribution:** https://www.openstreetmap.org/copyright  
**File:** `data/vadodara_road_network.geojson` (~35 MB)

> ⚠️ OSM provides **geographic road data ONLY** — no traffic volume, vehicle counts, or congestion. Traffic data comes from `traffic_records` (23,048 records).

### Dataset Stats

| Metric | Value |
|---|---|
| Total features in file | 45,909 |
| LineString roads imported | **45,903** |
| Polygon areas (skipped) | 6 |
| Roads with names | 898 (~2%) |
| One-way roads | 2,698 |
| Bridges | 1,088 |
| Tunnels | 95 |

### Database Table: `road_network`

```sql
CREATE TABLE road_network (
    id            SERIAL PRIMARY KEY,
    osm_id        VARCHAR(30) NOT NULL UNIQUE,
    highway_type  VARCHAR(50) NOT NULL,
    road_name     VARCHAR(300),
    ref           VARCHAR(50),
    lanes         INTEGER,
    maxspeed      INTEGER,
    oneway        BOOLEAN NOT NULL DEFAULT FALSE,
    surface       VARCHAR(50),
    bridge        BOOLEAN NOT NULL DEFAULT FALSE,
    tunnel        BOOLEAN NOT NULL DEFAULT FALSE,
    road_length_m FLOAT,
    geometry_json JSONB NOT NULL,
    imported_at   TIMESTAMP WITH TIME ZONE NOT NULL
);
```

> Geometry stored as **JSONB** (PostGIS not available). Supports full geometry retrieval for map rendering.

### Road Network API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/road-network/stats` | Dataset statistics (totals, breakdown by highway type) |
| `GET /api/road-network/geojson` | GeoJSON FeatureCollection for map rendering |
| `GET /api/road-network` | Paginated list WITHOUT geometry |
| `GET /api/road-network/{id}` | Single road WITH full geometry |

### How to Import / Re-Import

```bash
cd backend
source venv/bin/activate

# Dry run (validate only):
python import_vadodara_roads.py --dry-run

# Live import:
python import_vadodara_roads.py
```

Import uses `ON CONFLICT DO NOTHING` — safe to re-run. Existing rows are silently skipped.

---

## 15. Database Schema & Status

### Tables

| Table | Description | Records |
|-------|-------------|---------|
| `users` | Operator/admin accounts | 6 |
| `junctions` | Traffic intersection data | 8 |
| `traffic_records` | Historical traffic sensor data | **23,048 ✅** |
| `signal_timings` | Signal configuration | 1 |
| `ai_recommendations` | AI-generated recommendations | varies |
| `emergency_routes` | Emergency routing history | varies |
| `operator_logs` | Immutable audit trail | grows with use |
| `road_network` | OSM road segments | **45,903** |

> ⚠️ **CRITICAL:** The `traffic_records` table (23,048 Vadodara records) must never be truncated or modified. Only truncate `road_network` if re-importing OSM data.

### Migration (Alembic)

```bash
cd backend && source venv/bin/activate

# Check current migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

---

## 16. API Endpoints & CRUD

**Base URL:** `http://localhost:8000`  
**Swagger UI:** `http://localhost:8000/docs`

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/login` | Login, receive JWT | ❌ Public |
| GET | `/api/auth/me` | Get current user | ✅ JWT |

### Junctions
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/junctions` | ✅ JWT |
| GET | `/api/junctions/{id}` | ✅ JWT |
| POST | `/api/junctions` | ✅ JWT |
| PUT | `/api/junctions/{id}` | ✅ JWT |
| DELETE | `/api/junctions/{id}` | ✅ JWT |

### Traffic Records
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/api/traffic-records` | Paginated |
| GET | `/api/traffic-records/summary` | Aggregated per junction |
| GET | `/api/traffic-records/{id}` | Single record |
| POST | `/api/traffic-records` | ✅ JWT |
| DELETE | `/api/traffic-records/{id}` | ✅ JWT |

### AI Recommendations
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/api/ai-recommendations` | Filter by status |
| GET | `/api/ai-recommendations/{id}` | |
| POST | `/api/ai-recommendations/generate` | ✅ JWT — triggers rule engine |
| POST | `/api/ai-recommendations` | ✅ JWT |
| PUT | `/api/ai-recommendations/{id}` | ✅ JWT — approve/reject |
| DELETE | `/api/ai-recommendations/{id}` | ✅ JWT |

### Emergency Routes
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/emergency-routes` | ✅ JWT |
| GET | `/api/emergency-routes/{id}` | ✅ JWT |
| POST | `/api/emergency-routes` | ✅ JWT |
| PUT | `/api/emergency-routes/{id}` | ✅ JWT |

### Operator Logs
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/api/operator-logs` | ✅ JWT — immutable audit trail |
| GET | `/api/operator-logs/{id}` | ✅ JWT |

### Users (Admin)
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/users` | ✅ JWT |
| GET | `/api/users/{id}` | ✅ JWT |
| POST | `/api/users` | ✅ JWT + Admin only |
| PUT | `/api/users/{id}` | ✅ JWT + Admin only |
| DELETE | `/api/users/{id}` | ✅ JWT + Admin only |

### Road Network
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/api/road-network/stats` | Public |
| GET | `/api/road-network/geojson` | Query params: `highway_type`, `limit`, `oneway` |
| GET | `/api/road-network` | Paginated list (no geometry) |
| GET | `/api/road-network/{id}` | Single road with geometry |

---

## 17. Testing & Verification

### Backend Automated Tests

```bash
cd backend
source venv/bin/activate

python test_api.py            # Full API test suite
python test_business_logic.py # Business logic verification
python test_ai_engine.py      # AI recommendation engine tests
```

**Results (All Pass):**

| Suite | Status |
|-------|--------|
| test_api.py | ✅ ALL PASS |
| test_business_logic.py | ✅ ALL PASS |
| test_ai_engine.py | ✅ ALL PASS |

### Frontend Build

```bash
npm run build
```

**Result:** ✅ ZERO errors — 2419 modules transformed in ~321ms

### API Authentication Tests

| Test | Expected | Result |
|------|----------|--------|
| Valid login (j.sharma) | 200 + JWT | ✅ PASS |
| Invalid password | 401 | ✅ PASS |
| Empty fields | 422 | ✅ PASS |
| GET /api/auth/me (valid token) | 200 | ✅ PASS |
| GET /api/auth/me (no token) | 401 | ✅ PASS |
| POST without auth | 401 | ✅ PASS |
| POST new user (non-admin) | 403 | ✅ PASS |

### Database Integrity (Final State)

| Table | Before | After | Δ |
|-------|--------|-------|---|
| users | 6 | 6 | 0 |
| junctions | 8 | 8 | 0 |
| **traffic_records** | **23,048** | **23,048** | **0 ✅** |
| signal_timings | 1 | 1 | 0 |
| ai_recommendations | 13 | 13 | 0 (test rec created+deleted) |
| emergency_routes | 5 | 5 | 0 |
| operator_logs | 21 | 26 | +5 (legitimate audit entries) |
| road_network | 45,903 | 45,903 | 0 |

> Operator log increase (+5) is **expected** — approving/rejecting recommendations creates audit entries.

### Mock Data Audit

| Usage | Classification | Status |
|-------|---------------|--------|
| `vehicleMovement` in Analytics.jsx | DEMO PROTOTYPE — labelled as placeholder | Acceptable |
| `assistantSeedMessages` in Assistant.jsx | DEMO — AI assistant is prototype feature | Acceptable |
| Dashboard data | REAL (PostgreSQL via API) | ✅ |
| Decision Queue data | REAL (PostgreSQL via API) | ✅ |
| Traffic Map data | REAL (PostgreSQL via API) | ✅ |

---

## 18. Development Phases

| Phase | Status | Scope |
|---|---|---|
| **Phase 1** | ✅ Complete | Frontend layouts, UI design, form structures, CSS Modules, mock data |
| **Phase 2** | ✅ Complete | FastAPI backend, PostgreSQL schema, seed data, REST APIs, Alembic |
| **Phase 3** | ✅ Complete | Traffic data integration (23,048 Vadodara records), Decision Queue, CRUD |
| **Phase 4** | ✅ Complete | JWT authentication, operator logging, TomTom map, bug fixes |
| **Phase 5** | ✅ Complete | Rule-based AI engine, generate recommendations endpoint, testing |

### Key Changes Per Phase

**Phase 4 Fixes Applied:**

| # | Issue | Fix | File |
|---|-------|-----|------|
| 1 | TomTom tile URL used v2 (404) | Corrected to v1 (200 OK) | TrafficMap.jsx |
| 2 | maplibre-gl import crashed Vite | Switched to CDN script tag | index.html |
| 3 | Vite died after start.sh exited | Used `nohup` daemonize pattern | start.sh |
| 4 | `reviewed_by` hardcoded | Backend uses `current_user.id` | DecisionQueue.jsx |
| 5 | `password_hash: 'placeholder_hash'` | Backend auto-hashes to bcrypt | api.js |
| 6 | GET /api/users had no auth | Added `get_current_user` dependency | users.py |

---

## 19. Performance Report

**Dashboard Load Time (5 Runs):**

| Run | Total API Time (parallel) |
|-----|--------------------------|
| 1 | 114 ms |
| 2 | 119 ms |
| 3 | 109 ms |
| 4 | 111 ms |
| 5 | 113 ms |
| **Average** | **~113 ms** |

**Why fast:**
- `Promise.all` for 4 parallel API calls ✅
- Aggregated backend query (not raw 23,048 records) ✅
- Single `useEffect` + `useCallback` — no duplicate calls ✅
- JWT validation is O(1) ✅

**Root Cause of Previous Perceived Lag:** Vite server instability (process dying after startup) — fixed with `nohup` daemon pattern in `start.sh`.

---

## 20. Project Status

**Date:** 22 September 2026  
**Status: ✅ COMPLETE — READY FOR SUBMISSION**

### Services

| Service | URL | Status |
|---------|-----|--------|
| Frontend (Vite) | http://localhost:5173 | ✅ Running |
| Backend (FastAPI) | http://localhost:8000 | ✅ Running |
| API Docs (Swagger) | http://localhost:8000/docs | ✅ Running |
| PostgreSQL | localhost:5432/signalai | ✅ Connected |
| TomTom Map | api.tomtom.com/map/1 | ✅ 200 OK |

### Faculty Requirements Checklist

| Requirement | Status |
|---|---|
| Complete source code | ✅ PASS |
| Functional UI/forms | ✅ PASS |
| Database connectivity (PostgreSQL) | ✅ PASS |
| CRUD operations | ✅ PASS |
| Code documentation/comments | ✅ PASS |
| Database schema and structure | ✅ PASS |
| README + installation guide | ✅ PASS (this file) |
| Progress documentation | ✅ PASS |
| Error handling | ✅ PASS |
| Organized folder structure | ✅ PASS |
| Database backup/setup script | ✅ PASS |
| Testing (automated + manual) | ✅ PASS |
| Code runs successfully | ✅ PASS |

---

## 21. Faculty Demo Guide

**Demo URL:** http://localhost:5173  
**Login:** `j.sharma@signalai.gov.in` / `password123`

### Quick Start

```bash
bash start.sh
# Open browser to: http://localhost:5173
```

### Step-by-Step Demo Workflow

**1. Login**
- Navigate to http://localhost:5173
- Enter email: `j.sharma@signalai.gov.in` / password: `password123`
- ✅ Verify: JWT generated, user name shown in header

**2. Dashboard**
- ✅ KPI cards: 8 junctions, traffic density, congested count
- ✅ Traffic trend chart using real PostgreSQL aggregated data
- ✅ Pending AI recommendations listed
- ✅ Recent operator activity log (last 5 entries)

**3. Traffic Map (TomTom)**
- ✅ TomTom basemap loads over Vadodara, India
- ✅ 8 colored junction markers at precise GPS coordinates
- ✅ Hover → popup shows junction name | Click → detail panel opens
- ✅ Search filter: type "Genda" → shows only J-101
- ✅ Status filter: click "Congested" → shows only red junctions

**4. Analytics**
- ✅ Charts render (Recharts library)
- ✅ Traffic trends, peak hour, junction comparison from real data
- ⚠️ `vehicleMovement` area chart uses demo placeholder (labelled)

**5. Decision Queue — Generate AI Recommendations**
- Click **Run AI Engine** button
- ✅ Rule-based engine analyzes 8 junctions
- ✅ New recommendations appear in Pending tab
- ✅ Skips junctions already with PENDING recommendations

**6. Decision Queue — Approve / Reject**
- Click a PENDING recommendation → click **Approve**
- ✅ Status changes to APPROVED in database
- ✅ Operator log entry created with authenticated user's ID
- To reject: click another PENDING → **Reject** → enter reason → confirm

**7. Emergency Routing**
- ✅ Existing routes load from database
- ✅ Form available to create new routes
- ✅ Activate/deactivate/complete status management

**8. Admin Users (Login as Administrator)**
- Logout → Login as `r.mehta@signalai.gov.in` / `password123`
- ✅ All 6 users listed with roles and status
- ✅ Create new user (INACTIVE by default)
- ✅ Edit existing user role/status
- ✅ Delete test users
- Non-admin trying to create user → 403 Forbidden

**9. Settings**
- ✅ Shows currently authenticated user's name and role
- ✅ No hardcoded placeholder profile

**10. Logout**
- ✅ JWT cleared from localStorage
- ✅ Redirected to /login
- Navigate manually to `/dashboard` → ✅ Redirected back to /login

### Database Verification

```bash
cd backend
source venv/bin/activate
python3 -c "
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
for t in ['users','junctions','traffic_records','signal_timings','ai_recommendations']:
    print(t, db.execute(text(f'SELECT COUNT(*) FROM {t}')).scalar())
db.close()
" 2>/dev/null
```

Expected: `traffic_records 23048`

### Stopping the Application

```bash
bash stop.sh
```

---

## 22. Scripts

```bash
npm run dev       # Start dev server at http://localhost:5173
npm run build     # Build production bundle → /dist (ZERO errors)
npm run preview   # Preview production build locally
npm run lint      # Run OxLint static analysis on source files
```

```bash
bash start.sh     # Start PostgreSQL + Backend + Frontend
bash stop.sh      # Stop all services
```

---

## 23. Future Scope & Limitations

### Current Limitations

- **No real-time WebSockets** — dashboard refresh is manual
- **No physical hardware control** — SignalAI is a decision-support prototype, not a real signal controller
- **No PostGIS** — road geometry stored as JSONB; spatial queries (bounding-box filter, ST_Intersects) not available
- **No road-to-traffic linkage** — OSM roads and junction traffic records kept deliberately separate (requires PostGIS for proper GIS join)
- **Rule-Based AI only** — no machine learning or predictive models
- **AI Assistant is prototype** — uses static mock responses

### Future Development

- Integration with live IoT sensors and Edge AI camera nodes
- Transition from Rule-Based Engine to Predictive Machine Learning model (time-series forecasting)
- WebSockets for real-time dashboard updates
- PostGIS spatial queries and road-to-junction linkage
- Physical traffic signal hardware integration
- Password change API endpoint (currently UI-only)
- Mobile responsive design

---

## 👥 Project Info

| Field | Value |
|---|---|
| **Project Name** | SignalAI |
| **Version** | v4.0 (Phase 4 Final) |
| **Type** | BCA Mini Project |
| **System** | Municipal Traffic Control Portal |
| **Tech Stack** | React 18 + FastAPI + PostgreSQL + TomTom |
| **Location** | Vadodara, Gujarat, India |
| **Submission Date** | 22 September 2026 |

---

> ⚠️ **Disclaimer:** SignalAI is a **BCA academic prototype**. It does NOT control real traffic signals. All junction data and system statistics come from a real PostgreSQL database with 23,048 Vadodara traffic records. The system is a decision-support tool only.
