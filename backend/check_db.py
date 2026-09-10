import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.junction import Junction
from app.models.traffic_record import TrafficRecord
from app.models.signal_timing import SignalTiming
from app.models.ai_recommendation import AIRecommendation
from app.models.emergency_route import EmergencyRoute
from app.models.operator_log import OperatorLog

def check_db():
    db = SessionLocal()
    try:
        counts = {
            "users": db.query(User).count(),
            "junctions": db.query(Junction).count(),
            "traffic_records": db.query(TrafficRecord).count(),
            "signal_timings": db.query(SignalTiming).count(),
            "ai_recommendations": db.query(AIRecommendation).count(),
            "emergency_routes": db.query(EmergencyRoute).count(),
            "operator_logs": db.query(OperatorLog).count(),
        }
        for k, v in counts.items():
            print(f"{k}: {v}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
