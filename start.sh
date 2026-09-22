#!/bin/bash
# ============================================================
# SignalAI – One-command startup script
# Usage:  bash start.sh
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║          SignalAI Startup Script             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Kill any old processes on ports 5173 & 8000 ──
echo "► Stopping any previous servers..."
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
sleep 1
echo "  ✓ Ports 5173 and 8000 cleared"

# ── Step 2: Start Backend (FastAPI) ──
echo ""
echo "► Starting backend (FastAPI) on port 8000..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
  > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  ✓ Backend started (PID $BACKEND_PID)"

# Wait for backend to be ready
echo "  Waiting for backend to be ready..."
for i in {1..20}; do
  if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo "  ✓ Backend is healthy!"
    break
  fi
  sleep 1
  if [ $i -eq 20 ]; then
    echo "  ✗ Backend failed to start. Check backend.log"
    exit 1
  fi
done

# ── Step 3: Start Frontend (Vite) ──
echo ""
echo "► Starting frontend (Vite) on port 5173..."
cd "$PROJECT_DIR"
deactivate 2>/dev/null
nohup npm run dev -- --port 5173 --strictPort \
  > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
sleep 3
echo "  ✓ Frontend started (PID $FRONTEND_PID)"

# ── Done ──
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅  SignalAI is running!                    ║"
echo "║                                              ║"
echo "║  Frontend:  http://localhost:5173            ║"
echo "║  Backend:   http://localhost:8000            ║"
echo "║  API Docs:  http://localhost:8000/docs       ║"
echo "║                                              ║"
echo "║  Login credentials (all users):             ║"
echo "║    Email:    j.sharma@signalai.gov.in        ║"
echo "║    Password: password123                     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Logs:  backend.log | frontend.log"
echo "  Stop:  bash stop.sh"
echo ""
