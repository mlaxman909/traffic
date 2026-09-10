"""
backend/app/main.py
====================
SignalAI FastAPI Application Entry Point

This file:
1. Creates the FastAPI application instance
2. Configures CORS (allows React dev server at localhost:5173)
3. Registers all routers
4. Exposes Swagger at /docs and ReDoc at /redoc

To run the server (from the backend/ directory with venv activated):
    uvicorn app.main:app --reload --port 8000

API Base URL:  http://localhost:8000
Swagger UI:    http://localhost:8000/docs
ReDoc:         http://localhost:8000/redoc
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import get_settings
from app.routers import (
    health,
    users,
    junctions,
    traffic_records,
    signal_timings,
    ai_recommendations,
    emergency_routes,
    operator_logs,
    auth,
    road_network,
)

# ── Application Instance ──────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title="SignalAI API",
    description=(
        "**SignalAI — Smart Traffic Signal Optimization Platform**\n\n"
        "Backend REST API for the SignalAI municipal traffic management system.\n\n"
        "**Important:** SignalAI is a *decision-support* system. "
        "AI recommendations must be reviewed and approved by a human Traffic Operator "
        "before any action is taken. The system does NOT control signals automatically.\n\n"
        "**Phase 3:** Full CRUD backend operational — "
        "Traffic Records, Signal Timings, AI Recommendations, Emergency Routes, "
        "and Operator Logs APIs are all live. "
        "JWT authentication and AI engine are Phase 4."
    ),
    version=settings.app_version,
    # These paths expose the auto-generated API documentation
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allows the React Vite dev server (localhost:5173) to make API calls.
# In production, replace with the actual deployed frontend domain.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,        # e.g. http://localhost:5173
        "http://localhost:3000",       # Common alternative dev port
        "http://127.0.0.1:5173",       # Common alternative localhost
        "http://localhost:5174",       # Fallback Vite port
        "http://127.0.0.1:5174",       # Fallback Vite port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


# ── Global Exception Handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches any unhandled exception and returns a clean JSON error
    instead of exposing stack traces or database connection details.
    """
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "An unexpected server error occurred. Please contact the system administrator.",
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(users.router)
app.include_router(junctions.router)
app.include_router(traffic_records.router)
app.include_router(signal_timings.router)
app.include_router(ai_recommendations.router)
app.include_router(emergency_routes.router)
app.include_router(operator_logs.router)
app.include_router(auth.router)
app.include_router(road_network.router)


# ── Root Endpoint ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], include_in_schema=False)
def root():
    """Redirect hint — visitors to / see a friendly message."""
    return {
        "message": "SignalAI API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


# ── Startup Event ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    """
    Runs once when the server starts.
    Logs basic configuration info (without exposing secrets).
    """
    print("=" * 60)
    print(f"  SignalAI API v{settings.app_version} starting up")
    print(f"  Environment : {settings.app_env}")
    print(f"  Swagger UI  : http://localhost:8000/docs")
    print(f"  Health check: http://localhost:8000/api/health")
    print(f"  CORS origin : {settings.frontend_url}")
    print("=" * 60)
