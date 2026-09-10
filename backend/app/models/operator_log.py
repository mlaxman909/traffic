"""
backend/app/models/operator_log.py
====================================
SQLAlchemy model for the 'operator_logs' table.

Every significant action an operator performs is recorded here.
This is the system's audit trail — crucial for accountability
in a government traffic management platform.

Examples of logged actions:
- "APPROVED recommendation AI-9042 for junction J-101"
- "ACTIVATED emergency route for AMB-07"
- "CREATED user j.smith@signalai.gov.in"
- "DISABLED user k.singh@signalai.gov.in"
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class OperatorLog(Base):
    """
    An immutable audit log entry for an operator action.
    Maps to the 'operator_logs' table in PostgreSQL.

    These records should never be deleted — they are the accountability trail.
    """
    __tablename__ = "operator_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Which user performed the action
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Short action code, e.g. "APPROVE_RECOMMENDATION", "CREATE_USER"
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Which type of entity was affected, e.g. "ai_recommendation", "user", "junction"
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # The primary key of the affected entity
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Full human-readable description of what happened
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ── Relationships ────────────────────────────────────────────────────────
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        back_populates="operator_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<OperatorLog id={self.id} user_id={self.user_id} "
            f"action={self.action!r} at={self.created_at}>"
        )
