"""
backend/app/models/junction.py
==============================
SQLAlchemy model for the 'junctions' table.

A junction represents a physical road intersection equipped with
traffic signals that the SignalAI system monitors.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class JunctionStatus(str, enum.Enum):
    """
    Current congestion level at the junction.
    Maps directly to the red/yellow/green status used in the Phase 1 UI.
    """
    NORMAL   = "NORMAL"    # Low traffic — green in UI
    MODERATE = "MODERATE"  # Medium traffic — yellow in UI
    HIGH     = "HIGH"      # Heavy traffic — red in UI
    CRITICAL = "CRITICAL"  # Severe congestion — requires immediate attention


class Junction(Base):
    """
    Represents a monitored road intersection.
    Maps to the 'junctions' table in PostgreSQL.
    """
    __tablename__ = "junctions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Short human-readable code, e.g. "J-101"
    junction_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    # Full descriptive name, e.g. "Main St & 5th Ave"
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # GPS coordinates for map display
    latitude: Mapped[float | None]  = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[JunctionStatus] = mapped_column(
        SAEnum(JunctionStatus, name="junction_status"),
        nullable=False,
        default=JunctionStatus.NORMAL,
    )

    # Current traffic density as a percentage (0–100)
    traffic_density: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Current green phase duration in seconds
    current_green_time: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Simple weather description, e.g. "Light Rain, 27°C"
    weather_condition: Mapped[str | None] = mapped_column(String(100), nullable=True)

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

    # ── Relationships ────────────────────────────────────────────────────────
    # All traffic sensor readings at this junction
    traffic_records: Mapped[list["TrafficRecord"]] = relationship(  # noqa: F821
        "TrafficRecord",
        back_populates="junction",
        cascade="all, delete-orphan",
    )

    # All signal timing changes at this junction
    signal_timings: Mapped[list["SignalTiming"]] = relationship(  # noqa: F821
        "SignalTiming",
        back_populates="junction",
        cascade="all, delete-orphan",
    )

    # All AI recommendations generated for this junction
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(  # noqa: F821
        "AIRecommendation",
        back_populates="junction",
        cascade="all, delete-orphan",
    )

    # Emergency routes that originate from this junction
    emergency_routes_origin: Mapped[list["EmergencyRoute"]] = relationship(  # noqa: F821
        "EmergencyRoute",
        foreign_keys="EmergencyRoute.origin_junction_id",
        back_populates="origin_junction",
    )

    # Emergency routes that terminate at this junction
    emergency_routes_destination: Mapped[list["EmergencyRoute"]] = relationship(  # noqa: F821
        "EmergencyRoute",
        foreign_keys="EmergencyRoute.destination_junction_id",
        back_populates="destination_junction",
    )

    def __repr__(self) -> str:
        return f"<Junction id={self.id} code={self.junction_code!r} status={self.status}>"
