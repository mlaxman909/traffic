"""
backend/app/models/emergency_route.py
=======================================
SQLAlchemy model for the 'emergency_routes' table.

Records every emergency green-corridor activation.
Emergency services (Ambulance, Fire Service, Police) can request
a green wave through a series of junctions.

A human operator MUST authorize the corridor before it is activated.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EmergencyType(str, enum.Enum):
    """Type of emergency vehicle requesting priority."""
    AMBULANCE    = "AMBULANCE"
    FIRE_SERVICE = "FIRE_SERVICE"
    POLICE       = "POLICE"


class AuthorizationStatus(str, enum.Enum):
    """Has an operator authorized this route?"""
    PENDING    = "PENDING"     # Awaiting operator decision
    AUTHORIZED = "AUTHORIZED"  # Operator approved
    REJECTED   = "REJECTED"    # Operator denied


class RouteStatus(str, enum.Enum):
    """Current lifecycle state of the emergency route."""
    PLANNED   = "PLANNED"    # Created but not yet active
    ACTIVE    = "ACTIVE"     # Currently in progress
    COMPLETED = "COMPLETED"  # Vehicle has passed through
    CANCELLED = "CANCELLED"  # Route was cancelled


class EmergencyRoute(Base):
    """
    Represents an emergency vehicle green-corridor request and its status.
    Maps to the 'emergency_routes' table in PostgreSQL.
    """
    __tablename__ = "emergency_routes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    emergency_type: Mapped[EmergencyType] = mapped_column(
        SAEnum(EmergencyType, name="emergency_type"),
        nullable=False,
    )

    # The vehicle's callsign or ID, e.g. "AMB-07", "FIRE-E12"
    vehicle_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # Starting junction (the vehicle's entry point into the corridor)
    origin_junction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Ending junction (the vehicle's destination)
    destination_junction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Urgency level (1 = highest priority)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Human-readable description of the route, e.g. "J-101 → J-103 → J-105"
    route_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Estimated time for the vehicle to traverse the corridor (minutes)
    estimated_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    authorization_status: Mapped[AuthorizationStatus] = mapped_column(
        SAEnum(AuthorizationStatus, name="authorization_status"),
        nullable=False,
        default=AuthorizationStatus.PENDING,
    )

    status: Mapped[RouteStatus] = mapped_column(
        SAEnum(RouteStatus, name="route_status"),
        nullable=False,
        default=RouteStatus.PLANNED,
        index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Which operator created / authorized this route
    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────────────────────────
    origin_junction: Mapped["Junction"] = relationship(  # noqa: F821
        "Junction",
        foreign_keys=[origin_junction_id],
        back_populates="emergency_routes_origin",
    )

    destination_junction: Mapped["Junction"] = relationship(  # noqa: F821
        "Junction",
        foreign_keys=[destination_junction_id],
        back_populates="emergency_routes_destination",
    )

    created_by_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by],
        back_populates="created_emergency_routes",
    )

    def __repr__(self) -> str:
        return (
            f"<EmergencyRoute id={self.id} type={self.emergency_type} "
            f"vehicle={self.vehicle_id!r} status={self.status}>"
        )
