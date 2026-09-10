# SignalAI — Installation Guide

**Platform:** macOS  
**Project:** SignalAI – Smart Traffic Signal Optimization Platform  
**Phase:** 2/3 — Database Foundation

---

## Prerequisites

| Software | Version | Required |
|---|---|---|
| macOS | 12+ | ✅ |
| Python | 3.11+ (tested 3.14.6) | ✅ |
| Node.js | 18+ | ✅ |
| npm | 9+ | ✅ |
| PostgreSQL | 16+ (tested 18.6) | ✅ |

---

## Step 1 — Install PostgreSQL (Postgres.app)

**Postgres.app is the easiest option for macOS.**

1. Download from: **https://postgresapp.com/**
2. Move `Postgres.app` to your `/Applications` folder
3. Open the app — click **Initialize** to create your first database cluster
4. The app will run automatically in your menu bar

### Add psql to your PATH (required for command line use)

Open Terminal and run:

```bash
# Add Postgres.app bin directory to PATH permanently
echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Verify PostgreSQL is working

```bash
psql --version
# Expected: psql (PostgreSQL) 18.6 (Postgres.app)

pg_isready
# Expected: /tmp:5432 - accepting connections
```

> **Note:** Postgres.app uses your **macOS username** as the default PostgreSQL superuser.  
> No password is required for local connections.  
> Find your username: `whoami`

---

## Step 2 — Create the signalai Database

```bash
createdb signalai
```

Verify it was created:

```bash
psql -l
# You should see "signalai" in the list
```

---

## Step 3 — Apply the Database Schema

From the SignalAI project root:

```bash
psql -d signalai -f database/schema.sql
```

Expected output: 7 `CREATE TABLE` messages + indexes + triggers.

Verify tables:

```bash
psql -d signalai -c "\dt"
```

Expected:

```
 ai_recommendations
 emergency_routes
 junctions
 operator_logs
 signal_timings
 traffic_records
 users
```

---

## Step 4 — Load Demo Seed Data

```bash
psql -d signalai -f database/seed.sql
```

Expected output ends with a verification table showing:
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

## Step 5 — Set Up Python Virtual Environment

```bash
cd "/path/to/SignalAI/backend"
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)`.

---

## Step 6 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic, Alembic, python-dotenv.

---

## Step 7 — Configure the .env File

```bash
cp .env.example .env
```

Edit `.env` and set your macOS username:

```bash
# Find your username
whoami
```

Then update `.env`:

```
DATABASE_URL=postgresql://YOUR_MACOS_USERNAME@localhost:5432/signalai
APP_ENV=development
FRONTEND_URL=http://localhost:5173
```

**Example:** If `whoami` returns `sahilp4514`:
```
DATABASE_URL=postgresql://sahilp4514@localhost:5432/signalai
```

> **No password is needed** for Postgres.app local connections.

---

## Step 8 — Configure Alembic (Migration Tracking)

If tables are already created via schema.sql:

```bash
cd backend
source venv/bin/activate
alembic stamp head
```

This tells Alembic "the database is already up to date" without re-running any DDL.

For future schema changes:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

---

## Step 9 — Start the FastAPI Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Expected startup output:

```
============================================================
  SignalAI API v1.0.0 starting up
  Environment : development
  Swagger UI  : http://localhost:8000/docs
  Health check: http://localhost:8000/api/health
  CORS origin : http://localhost:5173
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## Step 10 — Verify Backend Health

Open your browser or use curl:

```bash
# API alive?
curl http://localhost:8000/api/health
# → {"status":"ok","service":"SignalAI API"}

# PostgreSQL connected?
curl http://localhost:8000/api/health/database
# → {"status":"ok","database":"connected"}
```

Or open: **http://localhost:8000/docs** (Swagger UI)

---

## Step 11 — Start the React Frontend

Open a **new Terminal window** (keep the backend running):

```bash
cd "/path/to/SignalAI"
npm install
npm run dev
```

Open: **http://localhost:5173**

> **Note:** The frontend currently uses mock data from Phase 1.  
> API integration with the backend is Phase 4.

---

## Step 12 — Verify the Full Stack

| Check | URL | Expected Response |
|---|---|---|
| React frontend | http://localhost:5173 | SignalAI login page |
| API alive | http://localhost:8000/api/health | `{"status":"ok"}` |
| DB connected | http://localhost:8000/api/health/database | `{"status":"ok","database":"connected"}` |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |
| List users | http://localhost:8000/api/users | JSON array of 6 users |
| List junctions | http://localhost:8000/api/junctions | JSON array of 8 junctions |

---

## Step 13 — Database Backup & Restore

### Create a backup

```bash
pg_dump -d signalai --no-owner --no-privileges -f database/signalai_backup.sql
```

### Restore from backup

```bash
createdb signalai_restored
psql -d signalai_restored -f database/signalai_backup.sql
```

An existing backup is included at: `database/signalai_backup.sql`

---

## Quick Reference — Daily Use

```bash
# ── Every development session ─────────────────────────────────
# 1. Open Postgres.app (from Applications or menu bar)
# 2. Start backend:
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# 3. Start frontend (new terminal):
cd .. && npm run dev

# ── psql shortcuts ────────────────────────────────────────────
psql -d signalai                    # Connect to database
\dt                                  # List tables
\d users                             # Describe users table
SELECT * FROM junctions;            # Query data
\q                                   # Quit psql
```

---

## Troubleshooting

### "psql: command not found"
```bash
echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### "database 'signalai' does not exist"
```bash
createdb signalai
psql -d signalai -f database/schema.sql
psql -d signalai -f database/seed.sql
```

### FastAPI shows "database: disconnected"
- Check Postgres.app is open and running (green indicator in menu bar)
- Check `.env` has the correct DATABASE_URL with your macOS username (`whoami`)
- Test connection: `psql -d signalai -c "SELECT 1;"`

### "FATAL: role 'postgres' does not exist"
Postgres.app uses your macOS username, not `postgres`.  
Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://YOUR_MACOS_USERNAME@localhost:5432/signalai
```

### "connection refused" on port 5432
Postgres.app is not running. Open it from Applications and click Initialize/Start.

---

## Notes for Faculty Evaluation

- This is a Phase 2/3 academic prototype
- The React frontend uses simulated Phase 1 mock data
- The backend API is fully operational with real PostgreSQL connectivity
- All CRUD operations are tested and working
- JWT authentication will be implemented in Phase 4
- SignalAI does **NOT** control real traffic signals — it is a decision-support prototype
- Seed data uses placeholder password hashes (real hashing is Phase 4)
