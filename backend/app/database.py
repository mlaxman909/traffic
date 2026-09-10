"""
backend/app/database.py
=======================
SignalAI – Database Configuration

Sets up the SQLAlchemy engine, session factory, and Base class.
All values are read from environment variables — never hardcoded.

Usage in FastAPI routes (dependency injection):
    def some_endpoint(db: Session = Depends(get_db)):
        ...
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from pydantic_settings import BaseSettings
from functools import lru_cache


# ── Settings ─────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    pydantic-settings reads from the .env file automatically.
    """
    database_url: str = "postgresql://postgres:password@localhost:5432/signalai"
    app_env: str = "development"
    app_name: str = "SignalAI API"
    app_version: str = "1.0.0"
    frontend_url: str = "http://localhost:5173"

    # JWT Settings
    jwt_secret_key: str = "change-this-in-development-to-a-secure-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"          # Load from backend/.env if present
        env_file_encoding = "utf-8"
        case_sensitive = False     # DATABASE_URL and database_url both work
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings (only reads .env once)."""
    return Settings()


# ── Engine ────────────────────────────────────────────────────────────────────

def create_db_engine():
    """
    Create the SQLAlchemy engine.
    pool_pre_ping=True tells SQLAlchemy to test the connection before use,
    which prevents stale connections after PostgreSQL restarts.
    """
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,       # Validate connections before handing them out
        pool_size=5,              # Keep 5 connections open
        max_overflow=10,          # Allow up to 10 extra connections under load
        echo=(settings.app_env == "development"),  # Log SQL only in dev mode
    )


engine = create_db_engine()


# ── Session Factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # Transactions must be committed explicitly
    autoflush=False,    # Don't flush automatically; we control when writes happen
)


# ── Declarative Base ──────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this Base.
    SQLAlchemy uses Base.metadata to know about every table.
    """
    pass


# ── FastAPI Dependency ────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency: yields a database session, then closes it.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            result = db.query(SomeModel).all()
            return result
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Connection Health Check ───────────────────────────────────────────────────

def check_database_connection() -> bool:
    """
    Test whether the database is reachable.
    Returns True if connected, False if not.
    Used by the /api/health/database endpoint.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False
