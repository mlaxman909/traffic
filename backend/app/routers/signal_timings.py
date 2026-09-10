"""
backend/app/routers/signal_timings.py
=======================================
Full CRUD endpoints for the SignalTiming entity.

Endpoints:
  GET    /api/signal-timings                       → List all timing records
  GET    /api/signal-timings/{id}                  → Get one record by ID
  GET    /api/signal-timings/junction/{junction_id} → All timings for a junction
  POST   /api/signal-timings                       → Create a new timing record
  PUT    /api/signal-timings/{id}                  → Update reason / timing values
  DELETE /api/signal-timings/{id}                  → Remove a timing record

Important:
  - junction_id is a required FK → junctions.id (CASCADE delete)
  - changed_by is optional FK → users.id (SET NULL on delete)
  - new_green_time must be ≥ 1 (enforced by schema + DB constraint)
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.signal_timing import SignalTiming
from app.models.junction import Junction
from app.models.user import User
from app.schemas.signal_timing import SignalTimingCreate, SignalTimingRead
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/signal-timings", tags=["Signal Timings"])


# ── GET /api/signal-timings ──────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[SignalTimingRead],
    summary="List all signal timing records",
    description=(
        "Returns all signal timing change records ordered by most recent first. "
        "Filter by junction_id. Paginated via skip/limit."
    ),
)
def list_signal_timings(
    skip:        int      = Query(default=0,   ge=0,   description="Records to skip"),
    limit:       int      = Query(default=100, ge=1, le=500, description="Max records to return"),
    junction_id: int | None = Query(default=None, description="Filter by junction DB id"),
    db: Session = Depends(get_db),
):
    query = db.query(SignalTiming)
    if junction_id is not None:
        query = query.filter(SignalTiming.junction_id == junction_id)
    return query.order_by(SignalTiming.changed_at.desc()).offset(skip).limit(limit).all()


# ── GET /api/signal-timings/junction/{junction_id} ──────────────────────────

@router.get(
    "/junction/{junction_id}",
    response_model=list[SignalTimingRead],
    summary="All timing changes for a specific junction",
    description="Returns the complete history of signal timing changes at a given junction.",
)
def list_timings_for_junction(junction_id: int, db: Session = Depends(get_db)):
    # Verify junction exists
    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={junction_id} not found.",
        )
    return (
        db.query(SignalTiming)
        .filter(SignalTiming.junction_id == junction_id)
        .order_by(SignalTiming.changed_at.desc())
        .all()
    )


# ── GET /api/signal-timings/{id} ────────────────────────────────────────────

@router.get(
    "/{timing_id}",
    response_model=SignalTimingRead,
    summary="Get a single signal timing record by ID",
    description="Returns one signal timing record. Returns 404 if not found.",
)
def get_signal_timing(timing_id: int, db: Session = Depends(get_db)):
    record = db.query(SignalTiming).filter(SignalTiming.id == timing_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signal timing with id={timing_id} not found.",
        )
    return record


# ── POST /api/signal-timings ─────────────────────────────────────────────────

@router.post(
    "",
    response_model=SignalTimingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new signal timing change",
    description=(
        "Creates a new signal timing record. "
        "junction_id must reference an existing junction. "
        "changed_by must reference an existing user (or omit for system changes). "
        "new_green_time must be ≥ 1 second."
    ),
)
def create_signal_timing(
    payload: SignalTimingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new signal timing change record.

    Error cases:
    - 404: junction_id does not exist
    - 404: changed_by user does not exist
    - 422: new_green_time < 1
    """
    # Validate junction FK
    junction = db.query(Junction).filter(Junction.id == payload.junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={payload.junction_id} not found. "
                   f"Cannot create signal timing for a non-existent junction.",
        )

    # Validate user FK if provided
    if payload.changed_by is not None:
        user = db.query(User).filter(User.id == payload.changed_by).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={payload.changed_by} not found. "
                       f"Cannot reference a non-existent operator.",
            )

    new_record = SignalTiming(
        junction_id=payload.junction_id,
        previous_green_time=payload.previous_green_time,
        new_green_time=payload.new_green_time,
        reason=payload.reason,
        changed_by=payload.changed_by,
        changed_at=datetime.now(timezone.utc),
    )

    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create signal timing record — check constraint violations.",
        ) from exc

    return new_record


# ── PUT /api/signal-timings/{id} ────────────────────────────────────────────

@router.put(
    "/{timing_id}",
    response_model=SignalTimingRead,
    summary="Update a signal timing record",
    description=(
        "Partial update of a signal timing record. "
        "Only the fields included in the request body are changed. "
        "Returns 404 if the record is not found."
    ),
)
def update_signal_timing(
    timing_id: int,
    payload: SignalTimingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partial update — validates FKs before applying changes."""
    record = db.query(SignalTiming).filter(SignalTiming.id == timing_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signal timing with id={timing_id} not found.",
        )

    # Re-validate junction FK if being changed
    if payload.junction_id != record.junction_id:
        junction = db.query(Junction).filter(Junction.id == payload.junction_id).first()
        if not junction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Junction with id={payload.junction_id} not found.",
            )

    # Re-validate user FK if being set
    if payload.changed_by is not None:
        user = db.query(User).filter(User.id == payload.changed_by).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={payload.changed_by} not found.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update signal timing — check constraint violations.",
        ) from exc

    return record


# ── DELETE /api/signal-timings/{id} ─────────────────────────────────────────

@router.delete(
    "/{timing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a signal timing record",
    description="Permanently removes a signal timing record. Returns 404 if not found.",
)
def delete_signal_timing(
    timing_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(SignalTiming).filter(SignalTiming.id == timing_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signal timing with id={timing_id} not found.",
        )
    db.delete(record)
    db.commit()
