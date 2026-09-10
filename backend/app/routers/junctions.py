"""
backend/app/routers/junctions.py
==================================
CRUD endpoints for the Junction entity.

Endpoints:
  GET    /api/junctions          → List all junctions
  GET    /api/junctions/{id}     → Get one junction by ID
  POST   /api/junctions          → Register a new junction
  PUT    /api/junctions/{id}     → Update junction data
  DELETE /api/junctions/{id}     → Remove a junction
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.junction import Junction
from app.models.user import User
from app.schemas.junction import (
    JunctionCreate,
    JunctionUpdate,
    JunctionRead,
    JunctionSummary,
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/junctions", tags=["Junctions"])


# ── GET /api/junctions ────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[JunctionSummary],
    summary="List all junctions",
    description="Returns all monitored junctions with current status and density.",
)
def list_junctions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    junctions = db.query(Junction).offset(skip).limit(limit).all()
    return junctions


# ── GET /api/junctions/{id} ───────────────────────────────────────────────────

@router.get(
    "/{junction_id}",
    response_model=JunctionRead,
    summary="Get junction by ID",
    description="Returns full junction details. Returns 404 if not found.",
)
def get_junction(junction_id: int, db: Session = Depends(get_db)):
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={junction_id} not found.",
        )
    return junction


# ── POST /api/junctions ───────────────────────────────────────────────────────

@router.post(
    "",
    response_model=JunctionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new junction",
    description="Adds a new junction to the monitored network. Returns 409 if junction_code already exists.",
)
def create_junction(
    payload: JunctionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new junction record.

    Error cases:
    - 409 Conflict: junction_code is already registered
    """
    existing = db.query(Junction).filter(
        Junction.junction_code == payload.junction_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Junction with code '{payload.junction_code}' already exists.",
        )

    new_junction = Junction(
        junction_code=payload.junction_code,
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status=payload.status,
        traffic_density=payload.traffic_density,
        current_green_time=payload.current_green_time,
        weather_condition=payload.weather_condition,
    )

    try:
        db.add(new_junction)
        db.commit()
        db.refresh(new_junction)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create junction — junction_code may already be in use.",
        )

    return new_junction


# ── PUT /api/junctions/{id} ───────────────────────────────────────────────────

@router.put(
    "/{junction_id}",
    response_model=JunctionRead,
    summary="Update junction data",
    description="Updates one or more fields on an existing junction. Returns 404 if not found.",
)
def update_junction(
    junction_id: int,
    payload: JunctionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partial update — only provided fields are changed."""
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={junction_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(junction, field, value)

    db.commit()
    db.refresh(junction)
    return junction


# ── DELETE /api/junctions/{id} ────────────────────────────────────────────────

@router.delete(
    "/{junction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a junction",
    description="Removes a junction and all its related records. Returns 404 if not found.",
)
def delete_junction(
    junction_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permanently deletes a junction.
    Because traffic_records, signal_timings, and ai_recommendations
    have CASCADE deletes, they will be removed automatically.
    """
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={junction_id} not found.",
        )

    db.delete(junction)
    db.commit()
