"""
backend/app/routers/ai_recommendations.py
==========================================
Full CRUD endpoints for the AIRecommendation entity.

Endpoints:
  GET    /api/ai-recommendations               → List all recommendations
  GET    /api/ai-recommendations/{id}          → Get one by ID
  GET    /api/ai-recommendations/junction/{id} → All recs for a junction
  POST   /api/ai-recommendations               → Create a new recommendation
  PUT    /api/ai-recommendations/{id}          → Update recommendation (e.g., approve/reject)
  DELETE /api/ai-recommendations/{id}          → Remove a recommendation

Important notes:
  - These are DATABASE CRUD endpoints only. There is NO AI engine.
  - Recommendations are manually created for demo/testing purposes.
  - The status field (PENDING/APPROVED/REJECTED) is set manually via PUT.
  - junction_id FK is CASCADE delete — deleting a junction removes its recs.
  - traffic_record_id FK is SET NULL on delete.
  - reviewed_by FK is SET NULL on delete.

SignalAI is a decision-support system — AI recommendations must be
approved by a human Traffic Operator before any action is taken.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.ai_recommendation import (
    AIRecommendation,
    RecommendationStatus,
    RecommendationSeverity,
)
from app.models.junction import Junction
from app.models.traffic_record import TrafficRecord
from app.models.user import User
from app.models.operator_log import OperatorLog
from app.schemas.ai_recommendation import (
    AIRecommendationCreate,
    AIRecommendationUpdate,
    AIRecommendationRead,
)
from app.services.auth import get_current_user
from app.services.recommendation_engine import generate_recommendations
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai-recommendations", tags=["AI Recommendations"])

class GenerateResponse(BaseModel):
    analyzed_junctions: int
    recommendations_generated: int
    skipped_duplicate: int
    details: list[str]

@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Rule-Based AI Engine to generate recommendations",
    description="Analyzes traffic records and generates new AI recommendations based on rule logic.",
)
def run_ai_engine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = generate_recommendations(db)
    return results


# ── GET /api/ai-recommendations ──────────────────────────────────────────────

@router.get(
    "",
    response_model=list[AIRecommendationRead],
    summary="List all recommendations",
    description=(
        "Returns recommendations ordered by created_at descending. "
        "Filter by status (PENDING/APPROVED/REJECTED), severity, or junction_id."
    ),
)
def list_recommendations(
    skip:        int                        = Query(default=0,   ge=0,   description="Records to skip"),
    limit:       int                        = Query(default=100, ge=1, le=500, description="Max to return"),
    junction_id: int | None                 = Query(default=None, description="Filter by junction ID"),
    rec_status:  RecommendationStatus | None = Query(default=None, alias="status",
                                                     description="Filter: PENDING, APPROVED, REJECTED"),
    severity:    RecommendationSeverity | None = Query(default=None,
                                                       description="Filter: LOW, MEDIUM, HIGH, CRITICAL"),
    db: Session = Depends(get_db),
):
    query = db.query(AIRecommendation)

    if junction_id is not None:
        query = query.filter(AIRecommendation.junction_id == junction_id)
    if rec_status is not None:
        query = query.filter(AIRecommendation.status == rec_status)
    if severity is not None:
        query = query.filter(AIRecommendation.severity == severity)

    return (
        query
        .order_by(AIRecommendation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── GET /api/ai-recommendations/junction/{junction_id} ──────────────────────

@router.get(
    "/junction/{junction_id}",
    response_model=list[AIRecommendationRead],
    summary="All recommendations for a specific junction",
    description="Returns all recommendations for the given junction, newest first.",
)
def list_recommendations_for_junction(junction_id: int, db: Session = Depends(get_db)):
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={junction_id} not found.",
        )
    return (
        db.query(AIRecommendation)
        .filter(AIRecommendation.junction_id == junction_id)
        .order_by(AIRecommendation.created_at.desc())
        .all()
    )


# ── GET /api/ai-recommendations/{id} ────────────────────────────────────────

@router.get(
    "/{rec_id}",
    response_model=AIRecommendationRead,
    summary="Get one recommendation by ID",
    description="Returns a single recommendation. Returns 404 if not found.",
)
def get_recommendation(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI recommendation with id={rec_id} not found.",
        )
    return rec


# ── POST /api/ai-recommendations ─────────────────────────────────────────────

@router.post(
    "",
    response_model=AIRecommendationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recommendation (database only — no AI engine)",
    description=(
        "Creates a new recommendation record in PENDING status. "
        "This is a database operation — recommendations are created manually for demo/testing. "
        "junction_id must reference an existing junction. "
        "traffic_record_id and reviewed_by are optional foreign keys."
    ),
)
def create_recommendation(
    payload: AIRecommendationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a recommendation record.

    Error cases:
    - 404: junction_id does not exist
    - 404: traffic_record_id does not exist (if provided)
    """
    # Validate junction FK
    junction = db.query(Junction).filter(Junction.id == payload.junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={payload.junction_id} not found.",
        )

    # Validate traffic_record FK if provided
    if payload.traffic_record_id is not None:
        tr = db.query(TrafficRecord).filter(
            TrafficRecord.id == payload.traffic_record_id
        ).first()
        if not tr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Traffic record with id={payload.traffic_record_id} not found.",
            )

    new_rec = AIRecommendation(
        junction_id=payload.junction_id,
        traffic_record_id=payload.traffic_record_id,
        recommendation_text=payload.recommendation_text,
        reason=payload.reason,
        current_green_time=payload.current_green_time,
        suggested_green_time=payload.suggested_green_time,
        severity=payload.severity,
        status=RecommendationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        reviewed_at=None,
        reviewed_by=None,
        rejection_reason=None,
    )

    try:
        db.add(new_rec)
        db.commit()
        db.refresh(new_rec)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create recommendation — check constraint violations.",
        ) from exc

    return new_rec


# ── PUT /api/ai-recommendations/{id} ─────────────────────────────────────────

@router.put(
    "/{rec_id}",
    response_model=AIRecommendationRead,
    summary="Update recommendation status (approve / reject)",
    description=(
        "Used by an operator to APPROVE or REJECT a PENDING recommendation. "
        "Updates status, reviewed_by (operator ID), and optionally rejection_reason. "
        "Sets reviewed_at automatically when status changes from PENDING."
    ),
)
def update_recommendation(
    rec_id: int,
    payload: AIRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update recommendation lifecycle state.

    Error cases:
    - 404: recommendation not found
    - 404: reviewed_by user not found (if provided)
    - 400: trying to review an already-reviewed recommendation (optional guard)
    """
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI recommendation with id={rec_id} not found.",
        )

    # Validate reviewed_by FK if provided
    if payload.reviewed_by is not None:
        user = db.query(User).filter(User.id == payload.reviewed_by).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User (reviewer) with id={payload.reviewed_by} not found.",
            )

    update_data = payload.model_dump(exclude_unset=True)

    # Auto-set reviewed_at when status changes away from PENDING
    if "status" in update_data and update_data["status"] != RecommendationStatus.PENDING:
        if rec.reviewed_at is None:
            rec.reviewed_at = datetime.now(timezone.utc)
        
        # Override the reviewed_by with the authenticated user
        update_data["reviewed_by"] = current_user.id
        
        # Create an operator log
        action_name = "APPROVE_RECOMMENDATION" if update_data["status"] == RecommendationStatus.APPROVED else "REJECT_RECOMMENDATION"
        log = OperatorLog(
            user_id=current_user.id,
            action=action_name,
            entity_type="ai_recommendation",
            entity_id=rec.id,
            description=f"Operator {current_user.name} marked recommendation {rec.id} as {update_data['status']}"
        )
        db.add(log)

    for field, value in update_data.items():
        setattr(rec, field, value)

    try:
        db.commit()
        db.refresh(rec)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update recommendation — check constraint violations.",
        ) from exc

    return rec


# ── DELETE /api/ai-recommendations/{id} ──────────────────────────────────────

@router.delete(
    "/{rec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recommendation",
    description="Permanently removes a recommendation. Returns 404 if not found.",
)
def delete_recommendation(
    rec_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI recommendation with id={rec_id} not found.",
        )
    db.delete(rec)
    db.commit()
