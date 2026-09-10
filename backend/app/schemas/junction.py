"""
backend/app/schemas/junction.py
=================================
Pydantic schemas for the Junction entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.junction import JunctionStatus


class JunctionCreate(BaseModel):
    """Data required to register a new monitored junction."""
    junction_code:    str           = Field(..., min_length=1, max_length=20,
                                           description="Unique code, e.g. 'J-101'")
    name:             str           = Field(..., min_length=2, max_length=200,
                                           description="Full name, e.g. 'Main St & 5th Ave'")
    latitude:         float | None  = Field(default=None, ge=-90,  le=90)
    longitude:        float | None  = Field(default=None, ge=-180, le=180)
    status:           JunctionStatus = Field(default=JunctionStatus.NORMAL)
    traffic_density:  int | None    = Field(default=None, ge=0, le=100,
                                           description="Current congestion %")
    current_green_time: int | None  = Field(default=None, ge=0,
                                            description="Green phase duration in seconds")
    weather_condition:  str | None  = Field(default=None, max_length=100)


class JunctionUpdate(BaseModel):
    """All fields optional — used for partial updates (PUT)."""
    name:              str | None          = Field(default=None, min_length=2, max_length=200)
    latitude:          float | None        = Field(default=None, ge=-90,  le=90)
    longitude:         float | None        = Field(default=None, ge=-180, le=180)
    status:            JunctionStatus | None = Field(default=None)
    traffic_density:   int | None          = Field(default=None, ge=0, le=100)
    current_green_time: int | None         = Field(default=None, ge=0)
    weather_condition:  str | None         = Field(default=None, max_length=100)


class JunctionRead(BaseModel):
    """Full junction data returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id:                 int
    junction_code:      str
    name:               str
    latitude:           float | None
    longitude:          float | None
    status:             JunctionStatus
    traffic_density:    int | None
    current_green_time: int | None
    weather_condition:  str | None
    created_at:         datetime
    updated_at:         datetime


class JunctionSummary(BaseModel):
    """Compact junction representation for list views / map overlays."""
    model_config = ConfigDict(from_attributes=True)

    id:              int
    junction_code:   str
    name:            str
    status:          JunctionStatus
    traffic_density: int | None
    latitude:        float | None
    longitude:       float | None
