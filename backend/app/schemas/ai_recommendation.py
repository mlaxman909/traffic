"""
backend/app/schemas/ai_recommendation.py
==========================================
Pydantic schemas for the AIRecommendation entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.ai_recommendation import (
    RecommendationStatus,
    RecommendationSeverity,
)


class AIRecommendationCreate(BaseModel):
    junction_id:          int                      = Field(..., description="Junction this applies to")
    traffic_record_id:    int | None               = Field(default=None)
    recommendation_text:  str                      = Field(..., min_length=10,
                                                           description="Human-readable suggested action")
    reason:               str | None               = Field(default=None,
                                                          description="Data-driven explanation")
    current_green_time:   int | None               = Field(default=None, ge=0)
    suggested_green_time: int | None               = Field(default=None, ge=0)
    severity:             RecommendationSeverity   = Field(default=RecommendationSeverity.MEDIUM)


class AIRecommendationUpdate(BaseModel):
    """Used when an operator approves or rejects a recommendation."""
    status:           RecommendationStatus | None = Field(default=None)
    reviewed_by:      int | None                  = Field(default=None,
                                                          description="Operator ID who reviewed")
    rejection_reason: str | None                  = Field(default=None)


class AIRecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                   int
    junction_id:          int
    traffic_record_id:    int | None
    recommendation_text:  str
    reason:               str | None
    current_green_time:   int | None
    suggested_green_time: int | None
    severity:             RecommendationSeverity
    status:               RecommendationStatus
    created_at:           datetime
    reviewed_at:          datetime | None
    reviewed_by:          int | None
    rejection_reason:     str | None
