"""
Alembic environment configuration for SignalAI.

This file tells Alembic:
1. How to connect to the database (reads DATABASE_URL from .env)
2. Which models exist (imports all models via app.models)
3. How to generate/apply migrations

Usage:
  # Create a new migration:
  alembic revision --autogenerate -m "describe what changed"

  # Apply all pending migrations:
  alembic upgrade head

  # Roll back one migration:
  alembic downgrade -1
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Make sure Python can find our app package ────────────────────────────────
# Alembic runs from the backend/ directory, so we add it to sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Import application components ────────────────────────────────────────────
from app.database import Base, get_settings  # noqa: E402
import app.models  # noqa: E402, F401  — Must import to register all models with Base.metadata

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use our SQLAlchemy metadata so Alembic can see all tables
target_metadata = Base.metadata

# ── Read database URL from environment ────────────────────────────────────────
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


# ── Migration functions ────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL statements without actually connecting to the database.
    Useful for generating migration scripts to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the database and applies migrations directly.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# ── Run the appropriate mode ──────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
