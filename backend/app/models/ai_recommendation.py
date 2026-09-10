"""
backend/app/models/ai_recommendation.py
=========================================
SQLAlchemy model for the 'ai_recommendations' table.

This is the CORE table of the SignalAI system.

The AI engine analyzes traffic data and generates recommendations.
Each recommendation must be reviewed and APPROVED or REJECTED by a
human Traffic Operator before any action is taken.

SignalAI is a decision-support system — AI never acts autonomously.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RecommendationStatus(str, enum.Enum):
    """Lifecycle state of an AI recommendation."""
    PENDING  = "PENDING"   # Waiting for operator review
    APPROVED = "APPROVED"  # Operator authorized the action
    REJECTED = "REJECTED"  # Operator declined the action


class RecommendationSeverity(str, enum.Enum):
    """How urgent the recommendation is."""
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class AIRecommendation(Base):
    """
    An AI-generated suggestion for adjusting signal timing at a junction.
    Maps to the 'ai_recommendations' table in PostgreSQL.

    Workflow:
    1. AI analyzes traffic data → creates recommendation (PENDING)
    2. Operator sees it in Decision Queue
    3. Operator approves → APPROVED + signal timing record created
    4. Operator rejects → REJECTED + rejection reason recorded
    """
    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    junction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional: the specific traffic snapshot that triggered this recommendation
    traffic_record_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("traffic_records.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Human-readable explanation of what the AI suggests
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Why the AI made this recommendation (data-driven explanation)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Current signal timing before the suggested change (seconds)
    current_green_time: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # What the AI recommends as the new green time (seconds)
    suggested_green_time: Mapped[int | None] = mapped_column(Integer, nullable=True)

    severity: Mapped[RecommendationSeverity] = mapped_column(
        SAEnum(RecommendationSeverity, name="recommendation_severity"),
        nullable=False,
        default=RecommendationSeverity.MEDIUM,
    )

    status: Mapped[RecommendationStatus] = mapped_column(
        SAEnum(RecommendationStatus, name="recommendation_status"),
        nullable=False,
        default=RecommendationStatus.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # When the operator made their decision
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Which operator reviewed it
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # If rejected, operator must provide a reason
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    junction: Mapped["Junction"] = relationship(  # noqa: F821
        "Junction",
        back_populates="ai_recommendations",
    )

    traffic_record: Mapped["TrafficRecord | None"] = relationship(  # noqa: F821
        "TrafficRecord",
        back_populates="ai_recommendations",
    )

    reviewer: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[reviewed_by],
        back_populates="reviewed_recommendations",
    )

    def __repr__(self) -> str:
        return (
            f"<AIRecommendation id={self.id} junction_id={self.junction_id} "
            f"severity={self.severity} status={self.status}>"
        )
