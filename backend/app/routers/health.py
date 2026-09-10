"""
backend/app/routers/health.py
================================
Health-check endpoints.

GET /api/health          → Always returns OK (checks that the server is running)
GET /api/health/database → Tests the PostgreSQL connection

These endpoints are safe to call without authentication.
They are used to verify the full stack:  React → FastAPI → PostgreSQL
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import check_database_connection

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get(
    "",
    summary="API health check",
    description="Returns OK if the FastAPI server is running.",
)
def health_check():
    """
    Basic liveness probe.
    Returns 200 OK as long as the server process is alive.
    Does NOT test the database connection.
    """
    return {"status": "ok", "service": "SignalAI API"}


@router.get(
    "/database",
    summary="Database connection check",
    description="Tests whether the FastAPI server can reach PostgreSQL.",
)
def database_health_check():
    """
    Readiness probe.
    Tests the PostgreSQL connection by executing 'SELECT 1'.
    Returns 200 if connected, 503 if not reachable.
    """
    connected = check_database_connection()

    if connected:
        return {"status": "ok", "database": "connected"}

    # Return 503 Service Unavailable — backend is up but DB is not
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "database": "disconnected",
            "detail": (
                "Cannot reach PostgreSQL. "
                "Ensure the database is running and DATABASE_URL in .env is correct."
            ),
        },
    )
