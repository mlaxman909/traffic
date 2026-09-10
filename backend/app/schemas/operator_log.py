"""
backend/app/schemas/operator_log.py
=====================================
Pydantic schemas for the OperatorLog entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OperatorLogCreate(BaseModel):
    user_id:     int | None = Field(default=None, description="ID of the operator")
    action:      str        = Field(..., min_length=1, max_length=100,
                                   description="Short action code, e.g. 'APPROVE_RECOMMENDATION'")
    entity_type: str | None = Field(default=None, max_length=50,
                                   description="Entity type affected, e.g. 'ai_recommendation'")
    entity_id:   int | None = Field(default=None, description="Primary key of affected entity")
    description: str | None = Field(default=None, description="Full human-readable description")


class OperatorLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    user_id:     int | None
    action:      str
    entity_type: str | None
    entity_id:   int | None
    description: str | None
    created_at:  datetime
