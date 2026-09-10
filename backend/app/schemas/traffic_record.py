"""
backend/app/schemas/traffic_record.py
=======================================
Pydantic schemas for the TrafficRecord entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.traffic_record import TrafficLevel


class TrafficRecordCreate(BaseModel):
    junction_id:            int          = Field(..., description="ID of the monitored junction")
    vehicles:               int | None   = Field(default=None, ge=0,
                                                 description="Vehicles per minute")
    traffic_level:          TrafficLevel = Field(default=TrafficLevel.LOW)
    congestion_percentage:  int | None   = Field(default=None, ge=0, le=100)
    recorded_at:            datetime | None = Field(
        default=None,
        description="When the reading was taken; defaults to current time if omitted"
    )


class TrafficRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                    int
    junction_id:           int
    recorded_at:           datetime
    vehicles:              int | None
    traffic_level:         TrafficLevel
    congestion_percentage: int | None
    created_at:            datetime
