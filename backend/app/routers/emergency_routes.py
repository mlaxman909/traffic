"""
backend/app/routers/emergency_routes.py
=========================================
Full CRUD endpoints for the EmergencyRoute entity.

Endpoints:
  GET    /api/emergency-routes               → List all emergency routes
  GET    /api/emergency-routes/{id}          → Get one by ID
  GET    /api/emergency-routes/active        → All currently ACTIVE routes
  POST   /api/emergency-routes               → Create a new route request
  PUT    /api/emergency-routes/{id}          → Update route status / authorization
  DELETE /api/emergency-routes/{id}          → Remove a route (RESTRICT FK protects junctions)

Important notes:
  - RESTRICT FK: origin_junction_id and destination_junction_id cannot reference
    non-existent junctions. The DB will reject invalid FKs.
  - Deleting a junction that is referenced by an active emergency route is BLOCKED
    at the DB level (ON DELETE RESTRICT).
  - This is NOT a real-time routing system. No GPS or live traffic optimization.
  - Operator authorization is required before a route can go ACTIVE (enforced
    at application level via authorization_status field).
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.emergency_route import EmergencyRoute, RouteStatus, AuthorizationStatus
from app.models.junction import Junction
from app.models.user import User
from app.models.operator_log import OperatorLog
from app.schemas.emergency_route import (
    EmergencyRouteCreate,
    EmergencyRouteUpdate,
    EmergencyRouteRead,
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/emergency-routes", tags=["Emergency Routes"])


# ── GET /api/emergency-routes ────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[EmergencyRouteRead],
    summary="List all emergency routes",
    description=(
        "Returns all emergency route requests ordered by created_at descending. "
        "Filter by status or authorization_status."
    ),
)
def list_emergency_routes(
    skip:                 int                    = Query(default=0,   ge=0,   description="Records to skip"),
    limit:                int                    = Query(default=100, ge=1, le=500, description="Max to return"),
    route_status:         RouteStatus | None     = Query(default=None, alias="status",
                                                         description="PLANNED/ACTIVE/COMPLETED/CANCELLED"),
    auth_status:          AuthorizationStatus | None = Query(
                                                         default=None, alias="authorization_status",
                                                         description="PENDING/AUTHORIZED/REJECTED"),
    db: Session = Depends(get_db),
):
    query = db.query(EmergencyRoute)

    if route_status is not None:
        query = query.filter(EmergencyRoute.status == route_status)
    if auth_status is not None:
        query = query.filter(EmergencyRoute.authorization_status == auth_status)

    return (
        query
        .order_by(EmergencyRoute.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── GET /api/emergency-routes/active ────────────────────────────────────────

@router.get(
    "/active",
    response_model=list[EmergencyRouteRead],
    summary="All currently active emergency routes",
    description="Shortcut endpoint — returns only routes with status=ACTIVE.",
)
def list_active_routes(db: Session = Depends(get_db)):
    return (
        db.query(EmergencyRoute)
        .filter(EmergencyRoute.status == RouteStatus.ACTIVE)
        .order_by(EmergencyRoute.created_at.desc())
        .all()
    )


# ── GET /api/emergency-routes/{id} ──────────────────────────────────────────

@router.get(
    "/{route_id}",
    response_model=EmergencyRouteRead,
    summary="Get one emergency route by ID",
    description="Returns a single emergency route. Returns 404 if not found.",
)
def get_emergency_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(EmergencyRoute).filter(EmergencyRoute.id == route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency route with id={route_id} not found.",
        )
    return route


# ── POST /api/emergency-routes ───────────────────────────────────────────────

@router.post(
    "",
    response_model=EmergencyRouteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new emergency route request",
    description=(
        "Creates a new emergency route in PLANNED status with PENDING authorization. "
        "origin_junction_id and destination_junction_id must reference existing junctions. "
        "created_by must reference an existing user (or omit for anonymous). "
        "Note: This does NOT activate the route — authorization must be updated via PUT."
    ),
)
def create_emergency_route(
    payload: EmergencyRouteCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Error cases:
    - 404: origin_junction_id does not exist
    - 404: destination_junction_id does not exist
    - 400: origin and destination are the same junction
    """
    # Validate that origin ≠ destination
    if payload.origin_junction_id == payload.destination_junction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Origin and destination junctions must be different.",
        )

    # Validate origin FK
    origin = db.query(Junction).filter(Junction.id == payload.origin_junction_id).first()
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Origin junction with id={payload.origin_junction_id} not found.",
        )

    # Validate destination FK
    destination = db.query(Junction).filter(
        Junction.id == payload.destination_junction_id
    ).first()
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination junction with id={payload.destination_junction_id} not found.",
        )

    new_route = EmergencyRoute(
        emergency_type=payload.emergency_type,
        vehicle_id=payload.vehicle_id,
        origin_junction_id=payload.origin_junction_id,
        destination_junction_id=payload.destination_junction_id,
        priority=payload.priority,
        route_description=payload.route_description,
        estimated_duration=payload.estimated_duration,
        created_by=current_user.id,
        authorization_status=AuthorizationStatus.PENDING,
        status=RouteStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )

    try:
        db.add(new_route)
        db.commit()
        db.refresh(new_route)
        
        # Log this critical action
        log = OperatorLog(
            user_id=current_user.id,
            action="CREATE_EMERGENCY_ROUTE",
            entity_type="emergency_route",
            entity_id=new_route.id,
            description=f"Operator {current_user.name} created an emergency route for {new_route.emergency_type} ({new_route.vehicle_id})"
        )
        db.add(log)
        db.commit()
        
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create emergency route — check constraint violations.",
        ) from exc

    return new_route


# ── PUT /api/emergency-routes/{id} ──────────────────────────────────────────

@router.put(
    "/{route_id}",
    response_model=EmergencyRouteRead,
    summary="Update emergency route status or authorization",
    description=(
        "Updates the authorization_status and/or route status. "
        "Use this to AUTHORIZE or REJECT a pending route, or to mark it ACTIVE/COMPLETED/CANCELLED. "
        "Returns 404 if not found."
    ),
)
def update_emergency_route(
    route_id: int,
    payload: EmergencyRouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    route = db.query(EmergencyRoute).filter(EmergencyRoute.id == route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency route with id={route_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(route, field, value)

    try:
        db.commit()
        db.refresh(route)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update emergency route — check constraint violations.",
        ) from exc

    return route


# ── DELETE /api/emergency-routes/{id} ────────────────────────────────────────

@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an emergency route",
    description=(
        "Permanently removes an emergency route record. "
        "Note: The referenced junctions are NOT deleted (FK is RESTRICT). "
        "Returns 404 if not found."
    ),
)
def delete_emergency_route(
    route_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    route = db.query(EmergencyRoute).filter(EmergencyRoute.id == route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency route with id={route_id} not found.",
        )
    try:
        db.delete(route)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete this emergency route due to a constraint conflict.",
        ) from exc
