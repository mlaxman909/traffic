"""
backend/app/schemas/signal_timing.py
======================================
Pydantic schemas for the SignalTiming entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SignalTimingCreate(BaseModel):
    junction_id:         int        = Field(..., description="ID of the junction")
    previous_green_time: int | None = Field(default=None, ge=0,
                                            description="Green time before change (seconds)")
    new_green_time:      int        = Field(..., ge=1,
                                           description="New green time (seconds)")
    reason:              str | None = Field(default=None,
                                           description="Why this timing was changed")
    changed_by:          int | None = Field(default=None,
                                           description="ID of operator who authorized this")


class SignalTimingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                  int
    junction_id:         int
    previous_green_time: int | None
    new_green_time:      int
    reason:              str | None
    changed_by:          int | None
    changed_at:          datetime
