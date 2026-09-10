import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models.traffic_record import TrafficRecord
from sqlalchemy import func

def check_traffic():
    db = SessionLocal()
    try:
        # get max, min, avg vehicles
        stats = db.query(
            func.min(TrafficRecord.vehicles),
            func.max(TrafficRecord.vehicles),
            func.avg(TrafficRecord.vehicles),
            func.min(TrafficRecord.congestion_percentage),
            func.max(TrafficRecord.congestion_percentage),
            func.avg(TrafficRecord.congestion_percentage),
        ).first()
        print(f"Vehicles - Min: {stats[0]}, Max: {stats[1]}, Avg: {stats[2]}")
        print(f"Congestion - Min: {stats[3]}, Max: {stats[4]}, Avg: {stats[5]}")

        # traffic levels distribution
        levels = db.query(TrafficRecord.traffic_level, func.count(TrafficRecord.id)).group_by(TrafficRecord.traffic_level).all()
        for level, count in levels:
            print(f"Level {level}: {count}")

    finally:
        db.close()

if __name__ == "__main__":
    check_traffic()
