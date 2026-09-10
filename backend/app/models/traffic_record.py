"""
backend/app/models/traffic_record.py
=====================================
SQLAlchemy model for the 'traffic_records' table.

Each record represents a snapshot of traffic conditions at a junction
at a specific point in time. This is where the Kaggle dataset will be
imported in Phase 3.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TrafficLevel(str, enum.Enum):
    """Categorical traffic level derived from congestion percentage."""
    LOW      = "LOW"      # < 40%
    MODERATE = "MODERATE" # 40–70%
    HIGH     = "HIGH"     # 70–90%
    CRITICAL = "CRITICAL" # > 90%


class TrafficRecord(Base):
    """
    A time-stamped traffic observation at a specific junction.
    Maps to the 'traffic_records' table in PostgreSQL.

    In Phase 1, equivalent data lives in mockData.js junctions array.
    In Phase 3, this table will be populated from the Kaggle dataset.
    """
    __tablename__ = "traffic_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Which junction this reading belongs to
    junction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # When this measurement was taken
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )

    # Number of vehicles passing through per minute
    vehicles: Mapped[int | None] = mapped_column(Integer, nullable=True)

    traffic_level: Mapped[TrafficLevel] = mapped_column(
        SAEnum(TrafficLevel, name="traffic_level"),
        nullable=False,
        default=TrafficLevel.LOW,
    )

    # Traffic density as a percentage (0–100)
    congestion_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────────────────────────
    junction: Mapped["Junction"] = relationship(  # noqa: F821
        "Junction",
        back_populates="traffic_records",
    )

    # AI recommendations generated from this traffic record
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(  # noqa: F821
        "AIRecommendation",
        back_populates="traffic_record",
    )

    def __repr__(self) -> str:
        return (
            f"<TrafficRecord id={self.id} junction_id={self.junction_id} "
            f"congestion={self.congestion_percentage}% at={self.recorded_at}>"
        )
