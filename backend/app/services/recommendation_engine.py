"""
backend/app/services/recommendation_engine.py
=============================================
Rule-Based AI Recommendation Engine (Phase 5).

Analyzes traffic records and generates signal timing recommendations.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.traffic_record import TrafficRecord
from app.models.junction import Junction
from app.models.ai_recommendation import AIRecommendation, RecommendationSeverity, RecommendationStatus

def generate_recommendations(db: Session) -> dict:
    """
    Analyzes the latest traffic records for each junction and generates recommendations
    based on a transparent rule engine.
    """
    results = {
        "analyzed_junctions": 0,
        "recommendations_generated": 0,
        "skipped_duplicate": 0,
        "details": []
    }

    # 1. Get all junctions
    junctions = db.query(Junction).all()
    
    for junction in junctions:
        # Get the latest traffic record for this junction
        latest_record = (
            db.query(TrafficRecord)
            .filter(TrafficRecord.junction_id == junction.id)
            .order_by(TrafficRecord.recorded_at.desc())
            .first()
        )

        if not latest_record:
            continue
            
        results["analyzed_junctions"] += 1
        
        # 2. Rule Engine Logic
        congestion = latest_record.congestion_percentage
        vehicles = latest_record.vehicles
        current_green = junction.current_green_time or 30
        
        suggested_green = current_green
        severity = None
        reason = None
        action_text = None
        
        # Time of day logic (naive approach based on recorded_at hour)
        hour = latest_record.recorded_at.hour
        if 7 <= hour <= 10:
            time_context = "morning peak"
        elif 16 <= hour <= 19:
            time_context = "evening peak"
        else:
            time_context = "off-peak hours"
            
        # Determine rules
        if congestion >= 80:
            severity = RecommendationSeverity.CRITICAL
            suggested_green = min(current_green + 20, 120) # Max 120s
            action_text = "significantly increasing"
            reason = f"Critical congestion ({congestion}%, {vehicles} vehicles) detected during {time_context}."
        elif congestion >= 60:
            severity = RecommendationSeverity.HIGH
            suggested_green = min(current_green + 10, 120)
            action_text = "increasing"
            reason = f"High congestion ({congestion}%, {vehicles} vehicles) detected during {time_context}."
        elif congestion <= 20:
            severity = RecommendationSeverity.LOW
            suggested_green = max(current_green - 10, 20) # Min 20s
            action_text = "decreasing"
            reason = f"Low traffic flow ({congestion}%, {vehicles} vehicles) during {time_context}."
            
        if severity is None or suggested_green == current_green:
            # No actionable recommendation
            continue
            
        recommendation_text = f"Junction {junction.junction_code} has {congestion}% congestion. Recommend {action_text} green time from {current_green}s to {suggested_green}s."
        
        # 3. Duplicate Prevention
        # Check if a pending recommendation already exists for this junction with the same severity
        existing_pending = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.junction_id == junction.id,
                AIRecommendation.status == RecommendationStatus.PENDING,
                AIRecommendation.severity == severity
            )
            .first()
        )
        
        if existing_pending:
            results["skipped_duplicate"] += 1
            continue
            
        # 4. Generate Recommendation
        new_rec = AIRecommendation(
            junction_id=junction.id,
            traffic_record_id=latest_record.id,
            recommendation_text=recommendation_text,
            reason=reason,
            current_green_time=current_green,
            suggested_green_time=suggested_green,
            severity=severity,
            status=RecommendationStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_rec)
        results["recommendations_generated"] += 1
        results["details"].append(recommendation_text)
        
    db.commit()
    return results
