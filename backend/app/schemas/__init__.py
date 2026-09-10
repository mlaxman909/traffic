"""
backend/app/schemas/__init__.py
=================================
Re-exports all Pydantic schemas for convenient importing.
"""

from app.schemas.user              import UserCreate, UserUpdate, UserRead, UserSummary
from app.schemas.junction          import JunctionCreate, JunctionUpdate, JunctionRead, JunctionSummary
from app.schemas.traffic_record    import TrafficRecordCreate, TrafficRecordRead
from app.schemas.signal_timing     import SignalTimingCreate, SignalTimingRead
from app.schemas.ai_recommendation import (
    AIRecommendationCreate,
    AIRecommendationUpdate,
    AIRecommendationRead,
)
from app.schemas.emergency_route   import (
    EmergencyRouteCreate,
    EmergencyRouteUpdate,
    EmergencyRouteRead,
)
from app.schemas.operator_log      import OperatorLogCreate, OperatorLogRead

__all__ = [
    "UserCreate", "UserUpdate", "UserRead", "UserSummary",
    "JunctionCreate", "JunctionUpdate", "JunctionRead", "JunctionSummary",
    "TrafficRecordCreate", "TrafficRecordRead",
    "SignalTimingCreate", "SignalTimingRead",
    "AIRecommendationCreate", "AIRecommendationUpdate", "AIRecommendationRead",
    "EmergencyRouteCreate", "EmergencyRouteUpdate", "EmergencyRouteRead",
    "OperatorLogCreate", "OperatorLogRead",
]
