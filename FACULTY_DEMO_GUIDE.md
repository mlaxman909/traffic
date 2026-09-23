# SignalAI — Faculty Demo Guide
## Phase 4 Final Submission Demo

**Date:** 22 September 2026  
**Demo URL:** http://localhost:5173  

---

## Quick Start

```bash
# Start everything:
cd "/Users/sahilp4514/Desktop/mini project/all code file"
bash start.sh

# Open browser to: http://localhost:5173
```

---

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Traffic Operator | j.sharma@signalai.gov.in | password123 |
| System Administrator | r.mehta@signalai.gov.in | password123 |
| Municipal Authority | s.gupta@municipal.gov.in | password123 |
| Emergency Service | a.khan@emergency.gov.in | password123 |

---

## End-to-End Demo Workflow

### 1. Login
- Navigate to http://localhost:5173
- Enter email: `j.sharma@signalai.gov.in` / password: `password123`
- Click **Authenticate & Enter**
- ✅ Verify: JWT generated, user name shown in header

### 2. Dashboard
- Automatically lands on Dashboard
- ✅ KPI cards: 8 junctions, traffic density, congested count
- ✅ Traffic trend chart using real PostgreSQL aggregated data
- ✅ Pending AI recommendations listed
- ✅ Recent operator activity log (last 5 entries)
- ✅ Refresh button reloads from database

### 3. Traffic Map (TomTom)
- Click **Traffic Map** in sidebar
- ✅ TomTom basemap loads over Vadodara, India
- ✅ 8 colored junction markers appear at precise GPS coordinates
  - Red = Congested (J-101, J-102, J-108)
  - Yellow = Moderate (J-103, J-104)  
  - Green = Low Traffic (J-105, J-106, J-107)
- ✅ Hover over a marker → popup shows junction code + name
- ✅ Click a marker → detail panel opens on right
- ✅ Detail panel shows: density, weather, coordinates, signal status
- ✅ Search filter: type "Genda" → shows only J-101
- ✅ Status filter: click "Congested" → shows only red junctions

### 4. Analytics
- Click **Analytics** in sidebar
- ✅ Charts render (Recharts library)
- ✅ Traffic trends, peak hour, junction comparison
- ⚠️ Note: `vehicleMovement` area chart uses demo data (clearly a prototype placeholder)
- ✅ Other charts use real data from PostgreSQL

### 5. Decision Queue — Generate AI Recommendation
- Click **Decision Queue** in sidebar
- Click **Run AI Engine** button
- ✅ Rule-based engine analyzes 8 junctions
- ✅ Generates recommendations based on traffic thresholds
- ✅ Skips junctions already with PENDING recommendations
- ✅ New recommendations appear in Pending tab

### 6. Decision Queue — Approve / Reject
- Click any PENDING recommendation
- Click **Approve** 
- ✅ Status changes to APPROVED in database
- ✅ Operator log entry created with authenticated user's ID
- ✅ Recommendation moves to Approved tab
- To reject: click another PENDING → click **Reject** → enter reason → confirm
- ✅ Status changes to REJECTED, rejection_reason saved

### 7. Operator Logs
- Check operator activity in Dashboard → Recent Activity
- Or review action trail in Decision Queue after approve/reject

### 8. Emergency Routing
- Click **Emergency Routing** in sidebar
- ✅ Existing 5 routes load from database
- ✅ Form available to create new routes
- ✅ Activate/deactivate status management

### 9. Admin Users (Login as Administrator)
- Logout → Login as `r.mehta@signalai.gov.in` / `password123`
- Click **Admin Users**
- ✅ All 6 users listed with roles and status
- ✅ Create new user (INACTIVE by default, password123 auto-set)
- ✅ Edit existing user role/status
- ✅ Delete test users
- Non-admin trying to create user → 403 Forbidden

### 10. Settings
- Click **Settings** in sidebar
- ✅ Shows currently authenticated user's name and role
- ✅ No hardcoded placeholder profile
- Password change form (UI only — backend endpoint is Phase 5)

### 11. Logout
- Click **Logout** in sidebar or header
- ✅ JWT cleared from localStorage
- ✅ Redirected to /login

### 12. Protected Route Access After Logout
- After logout, manually navigate to http://localhost:5173/dashboard
- ✅ Automatically redirected back to /login
- ✅ All routes protected by ProtectedRoute component

---

## Database Verification

```bash
cd "/Users/sahilp4514/Desktop/mini project/all code file/backend"
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

---

## API Documentation

Interactive API docs: http://localhost:8000/docs  
Health check: http://localhost:8000/api/health

---

## Stopping the Application

```bash
bash stop.sh
```
