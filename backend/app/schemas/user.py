"""
backend/app/schemas/user.py
=============================
Pydantic schemas for the User entity.

Three schema classes follow the standard pattern:
- UserCreate  : what the API expects when creating a user (POST)
- UserUpdate  : what the API accepts when editing a user (PUT) — all optional
- UserRead    : what the API returns — NEVER includes password_hash
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole, UserStatus


# ── Create ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """
    Data required to provision a new user.
    password_hash is set by a future auth service — for now a placeholder value is accepted.
    """
    name:     str      = Field(..., min_length=2, max_length=100,
                               description="Full name of the operator")
    email:    EmailStr = Field(..., description="Unique email address — used as login ID")
    password_hash: str = Field(
        default="placeholder_hash",
        description="Bcrypt hash of the password (Phase 1: placeholder accepted)"
    )
    role:     UserRole     = Field(default=UserRole.TRAFFIC_OPERATOR)
    status:   UserStatus   = Field(default=UserStatus.ACTIVE)
    district: str | None   = Field(default=None, max_length=100,
                                   description="City district this operator covers")


# ── Update ────────────────────────────────────────────────────────────────────

class UserUpdate(BaseModel):
    """
    Fields that can be changed on an existing user.
    All fields are optional — only provided fields are updated.
    """
    name:     str | None       = Field(default=None, min_length=2, max_length=100)
    email:    EmailStr | None  = Field(default=None)
    role:     UserRole | None  = Field(default=None)
    status:   UserStatus | None = Field(default=None)
    district: str | None       = Field(default=None, max_length=100)


# ── Read ──────────────────────────────────────────────────────────────────────

class UserRead(BaseModel):
    """
    Safe user representation returned by the API.
    Does NOT include password_hash.
    """
    model_config = ConfigDict(from_attributes=True)  # Allow ORM model → schema conversion

    id:         int
    name:       str
    email:      str
    role:       UserRole
    status:     UserStatus
    district:   str | None
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None


# ── Summary (for list views) ──────────────────────────────────────────────────

class UserSummary(BaseModel):
    """Compact user representation for list endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id:       int
    name:     str
    email:    str
    role:     UserRole
    status:   UserStatus
    district: str | None
