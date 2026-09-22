#!/bin/bash
# ============================================================
# SignalAI – Stop all servers
# Usage:  bash stop.sh
# ============================================================
echo "► Stopping SignalAI servers..."
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
echo "  ✓ All servers stopped"
