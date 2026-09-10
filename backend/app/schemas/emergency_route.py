"""
backend/app/schemas/emergency_route.py
========================================
Pydantic schemas for the EmergencyRoute entity.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.emergency_route import (
    EmergencyType,
    AuthorizationStatus,
    RouteStatus,
)


class EmergencyRouteCreate(BaseModel):
    emergency_type:           EmergencyType = Field(..., description="AMBULANCE / FIRE_SERVICE / POLICE")
    vehicle_id:               str           = Field(..., min_length=1, max_length=50,
                                                   description="Vehicle callsign, e.g. 'AMB-07'")
    origin_junction_id:       int           = Field(..., description="Starting junction ID")
    destination_junction_id:  int           = Field(..., description="Destination junction ID")
    priority:                 int           = Field(default=1, ge=1,
                                                   description="1 = highest priority")
    route_description:        str | None    = Field(default=None,
                                                   description="e.g. 'J-101 → J-103 → J-105'")
    estimated_duration:       int | None    = Field(default=None, ge=1,
                                                   description="Estimated minutes for transit")
    created_by:               int | None    = Field(default=None,
                                                   description="Operator ID who created this")


class EmergencyRouteUpdate(BaseModel):
    """Used to update authorization or route status."""
    authorization_status: AuthorizationStatus | None = Field(default=None)
    status:               RouteStatus | None         = Field(default=None)


class EmergencyRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                       int
    emergency_type:           EmergencyType
    vehicle_id:               str
    origin_junction_id:       int
    destination_junction_id:  int
    priority:                 int
    route_description:        str | None
    estimated_duration:       int | None
    authorization_status:     AuthorizationStatus
    status:                   RouteStatus
    started_at:               datetime | None
    completed_at:             datetime | None
    created_by:               int | None
    created_at:               datetime
