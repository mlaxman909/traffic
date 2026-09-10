"""
backend/app/models/user.py
==========================
SQLAlchemy model for the 'users' table.

Users are authorized personnel who can:
- Log into the SignalAI platform
- Review and approve/reject AI recommendations
- Authorize emergency routes
- Manage other users (System Administrators only)
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(str, enum.Enum):
    """System roles that determine what a user can do."""
    TRAFFIC_OPERATOR       = "TRAFFIC_OPERATOR"
    SYSTEM_ADMINISTRATOR   = "SYSTEM_ADMINISTRATOR"
    MUNICIPAL_AUTHORITY    = "MUNICIPAL_AUTHORITY"
    EMERGENCY_SERVICE      = "EMERGENCY_SERVICE"


class UserStatus(str, enum.Enum):
    """Whether the user account is currently active."""
    ACTIVE   = "ACTIVE"
    INACTIVE = "INACTIVE"


class User(Base):
    """
    Represents a registered system user.
    Maps to the 'users' table in PostgreSQL.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Bcrypt hash of the user's password — never store plaintext
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.TRAFFIC_OPERATOR,
    )

    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.ACTIVE,
    )

    # The city district this operator is assigned to
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────────────
    # One user can review many AI recommendations
    reviewed_recommendations: Mapped[list["AIRecommendation"]] = relationship(  # noqa: F821
        "AIRecommendation",
        foreign_keys="AIRecommendation.reviewed_by",
        back_populates="reviewer",
    )

    # One user can trigger many signal timing changes
    signal_timing_changes: Mapped[list["SignalTiming"]] = relationship(  # noqa: F821
        "SignalTiming",
        foreign_keys="SignalTiming.changed_by",
        back_populates="changed_by_user",
    )

    # One user can create many emergency routes
    created_emergency_routes: Mapped[list["EmergencyRoute"]] = relationship(  # noqa: F821
        "EmergencyRoute",
        foreign_keys="EmergencyRoute.created_by",
        back_populates="created_by_user",
    )

    # All actions this user has performed (audit log)
    operator_logs: Mapped[list["OperatorLog"]] = relationship(  # noqa: F821
        "OperatorLog",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
