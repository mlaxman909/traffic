# SignalAI Backend — README

**SignalAI API** · FastAPI · SQLAlchemy · PostgreSQL · Python 3.14

---

## Requirements

| Software | Version |
|---|---|
| Python | 3.11 or higher (tested on 3.14.6) |
| PostgreSQL | 16 (any modern version works) |
| pip | 23+ |

---

## 1. Install PostgreSQL

PostgreSQL must be installed and running before the backend can connect.

**macOS (EDB Installer):**
1. Download from https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Choose PostgreSQL 16 for macOS
3. Run the installer, set a superuser password, keep port 5432
4. After install, confirm: `psql --version`

**macOS (Postgres.app):**
1. Download from https://postgresapp.com/
2. Open the app, click "Initialize"
3. Follow instructions to add `psql` to PATH

---

## 2. Create the Database

Connect to PostgreSQL and create the `signalai` database:

```bash
psql -U postgres
```

Inside psql:

```sql
CREATE DATABASE signalai;
\q
```

---

## 3. Create the Virtual Environment

Run these commands from the `backend/` directory:

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL password:

```
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/signalai
```

---

## 6. Apply the Database Schema

```bash
psql -U postgres -d signalai -f ../database/schema.sql
```

---

## 7. (Optional) Load Seed Data

```bash
psql -U postgres -d signalai -f ../database/seed.sql
```

This loads demo data from the Phase 1 prototype (6 users, 8 junctions, etc.)

---

## 8. Run Database Migrations with Alembic

If using Alembic instead of raw SQL:

```bash
# Apply all pending migrations
alembic upgrade head
```

---

## 9. Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server starts at: `http://localhost:8000`

---

## 10. Verify Everything is Working

| URL | What it does |
|---|---|
| `http://localhost:8000/docs` | Swagger UI — interactive API docs |
| `http://localhost:8000/redoc` | ReDoc API documentation |
| `http://localhost:8000/api/health` | API liveness check |
| `http://localhost:8000/api/health/database` | PostgreSQL connection check |
| `http://localhost:8000/api/users` | List all users |
| `http://localhost:8000/api/junctions` | List all junctions |

---

## API Endpoints (Phase 2)

### Health
```
GET  /api/health              → API server status
GET  /api/health/database     → PostgreSQL connection status
```

### Users
```
GET    /api/users             → List all users
GET    /api/users/{id}        → Get user by ID
POST   /api/users             → Create new user
PUT    /api/users/{id}        → Update user
DELETE /api/users/{id}        → Delete user
```

### Junctions
```
GET    /api/junctions         → List all junctions
GET    /api/junctions/{id}    → Get junction by ID
POST   /api/junctions         → Register new junction
PUT    /api/junctions/{id}    → Update junction data
DELETE /api/junctions/{id}    → Remove junction
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py          ← FastAPI app, CORS, routers
│   ├── database.py      ← SQLAlchemy engine, session, Base
│   ├── models/          ← 7 SQLAlchemy ORM models
│   ├── schemas/         ← 7 Pydantic validation schemas
│   ├── routers/         ← API endpoints (health, users, junctions)
│   └── services/        ← Business logic (Phase 3)
├── alembic/             ← Database migration files
├── alembic.ini          ← Alembic configuration
├── requirements.txt     ← Python dependencies
├── .env.example         ← Environment variable template
└── README.md            ← This file
```

---

## Phase 3 (Not Yet Implemented)

- JWT authentication for all protected endpoints
- AI recommendation engine
- Kaggle traffic dataset import
- Full CRUD for all 7 tables
- Frontend API integration (replace mock data)
