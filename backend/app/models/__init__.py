"""
backend/app/models/__init__.py
================================
Imports all SQLAlchemy models so that:
1. SQLAlchemy metadata (Base.metadata) knows about every table.
2. Alembic can auto-detect all tables for migration generation.
3. app/main.py can do a single import to register everything.

IMPORTANT: Add any new model to both the import list and __all__.
"""

from app.models.user             import User, UserRole, UserStatus
from app.models.junction         import Junction, JunctionStatus
from app.models.traffic_record   import TrafficRecord, TrafficLevel
from app.models.signal_timing    import SignalTiming
from app.models.ai_recommendation import (
    AIRecommendation,
    RecommendationStatus,
    RecommendationSeverity,
)
from app.models.emergency_route  import (
    EmergencyRoute,
    EmergencyType,
    AuthorizationStatus,
    RouteStatus,
)
from app.models.operator_log     import OperatorLog
from app.models.road_network     import RoadNetwork

__all__ = [
    # Models
    "User",
    "Junction",
    "TrafficRecord",
    "SignalTiming",
    "AIRecommendation",
    "EmergencyRoute",
    "OperatorLog",
    "RoadNetwork",
    # Enums (exported so schemas can import from one place)
    "UserRole",
    "UserStatus",
    "JunctionStatus",
    "TrafficLevel",
    "RecommendationStatus",
    "RecommendationSeverity",
    "EmergencyType",
    "AuthorizationStatus",
    "RouteStatus",
]
