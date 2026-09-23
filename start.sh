#!/bin/bash
# ============================================================
# SignalAI – Bulletproof startup script
# Usage:  bash start.sh
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║          SignalAI Startup Script             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Kill ALL old processes on 5173/5174/8000 ──────────────────────────
echo "► Stopping any previous servers..."
lsof -ti:5173,5174,5175,8000 | xargs kill -9 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "uvicorn" 2>/dev/null
sleep 2
echo "  ✓ All old processes cleared"

# ── Step 2: Start Backend ──────────────────────────────────────────────────────
echo ""
echo "► Starting backend (FastAPI) on http://127.0.0.1:8000 ..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 \
  > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Wait for backend to respond
for i in {1..20}; do
  if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo "  ✓ Backend is healthy!"
    break
  fi
  sleep 1
  if [ $i -eq 20 ]; then
    echo "  ✗ Backend failed to start. See backend.log"
    exit 1
  fi
done

# ── Step 3: Start Frontend ─────────────────────────────────────────────────────
echo ""
echo "► Starting frontend (Vite) on http://localhost:5173 ..."
cd "$PROJECT_DIR"
deactivate 2>/dev/null

# Launch Vite fully detached (subshell + nohup = proper macOS daemon)
(nohup npx vite --port 5173 > "$PROJECT_DIR/frontend.log" 2>&1 &)

# Wait for Vite to respond
echo "  Waiting for Vite..."
FRONTEND_PID=""
for i in {1..20}; do
  sleep 1
  FRONTEND_PID=$(lsof -ti:5173 2>/dev/null | head -1)
  if curl -s --max-time 2 http://localhost:5173 > /dev/null 2>&1; then
    echo "  ✓ Frontend is up! (PID $FRONTEND_PID)"
    break
  fi
  if [ $i -eq 20 ]; then
    echo "  ✗ Frontend failed to start. Last log:"
    tail -25 "$PROJECT_DIR/frontend.log"
    exit 1
  fi
done

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅  SignalAI is LIVE!                       ║"
echo "║                                              ║"
echo "║  👉 Open: http://localhost:5173              ║"
echo "║                                              ║"
echo "║  Login:                                      ║"
echo "║    Email:    j.sharma@signalai.gov.in        ║"
echo "║    Password: password123                     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Logs:  tail -f frontend.log | backend.log"
echo "  Stop:  bash stop.sh"
echo ""
