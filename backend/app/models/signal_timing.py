"""
backend/app/models/signal_timing.py
====================================
SQLAlchemy model for the 'signal_timings' table.

Records every change made to a junction's green signal timing.
This provides an audit trail of who changed what and when.

Important: SignalAI is a DECISION-SUPPORT system.
Signal timing changes are recorded after a human operator approves
an AI recommendation — the system does NOT automatically change signals.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SignalTiming(Base):
    """
    Records a green-phase timing change at a junction.
    Maps to the 'signal_timings' table in PostgreSQL.
    """
    __tablename__ = "signal_timings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    junction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Green time before the change (in seconds)
    previous_green_time: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # New green time after the change (in seconds)
    new_green_time: Mapped[int] = mapped_column(Integer, nullable=False)

    # Why the timing was changed (typically references an AI recommendation)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Which operator authorized this change
    changed_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ── Relationships ────────────────────────────────────────────────────────
    junction: Mapped["Junction"] = relationship(  # noqa: F821
        "Junction",
        back_populates="signal_timings",
    )

    changed_by_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[changed_by],
        back_populates="signal_timing_changes",
    )

    def __repr__(self) -> str:
        return (
            f"<SignalTiming id={self.id} junction_id={self.junction_id} "
            f"{self.previous_green_time}s → {self.new_green_time}s>"
        )
