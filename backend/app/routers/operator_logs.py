"""
backend/app/routers/operator_logs.py
=======================================
Read + Append endpoints for the OperatorLog entity.

Endpoints:
  GET    /api/operator-logs              → List all logs (filterable, paginated)
  GET    /api/operator-logs/{id}         → Get one log entry by ID
  GET    /api/operator-logs/user/{uid}   → All logs for a specific user
  POST   /api/operator-logs              → Append a new log entry

IMPORTANT — Append-Only Design:
  Operator logs are the AUDIT TRAIL of the system.
  They document every significant operator action for accountability.
  As such:
  - PUT / PATCH are NOT implemented (logs must not be altered)
  - DELETE is NOT implemented (logs must not be erased)
  - Only GET (read) and POST (append) are supported.

  This matches the SQL schema comment:
  "Immutable audit trail. Do not delete rows."

If business requirements change in the future (e.g., GDPR compliance),
audit log management should be handled through a separate admin process,
not through this API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.operator_log import OperatorLog
from app.models.user import User
from app.schemas.operator_log import OperatorLogCreate, OperatorLogRead
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/operator-logs", tags=["Operator Logs"])


# ── GET /api/operator-logs ───────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[OperatorLogRead],
    summary="List all operator log entries",
    description=(
        "Returns audit log entries ordered by created_at descending (most recent first). "
        "Filter by user_id, action code, or entity_type. Paginated."
    ),
)
def list_operator_logs(
    skip:        int         = Query(default=0,   ge=0,   description="Records to skip"),
    limit:       int         = Query(default=100, ge=1, le=500, description="Max to return"),
    user_id:     int | None  = Query(default=None, description="Filter by operator user ID"),
    action:      str | None  = Query(default=None, description="Filter by action code, e.g. 'APPROVE_RECOMMENDATION'"),
    entity_type: str | None  = Query(default=None, description="Filter by entity type, e.g. 'ai_recommendation'"),
    db: Session = Depends(get_db),
):
    query = db.query(OperatorLog)

    if user_id is not None:
        query = query.filter(OperatorLog.user_id == user_id)
    if action is not None:
        query = query.filter(OperatorLog.action == action)
    if entity_type is not None:
        query = query.filter(OperatorLog.entity_type == entity_type)

    return (
        query
        .order_by(OperatorLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── GET /api/operator-logs/user/{user_id} ───────────────────────────────────

@router.get(
    "/user/{user_id}",
    response_model=list[OperatorLogRead],
    summary="All log entries for a specific operator",
    description="Returns all audit log entries for the given user, newest first.",
)
def list_logs_for_user(user_id: int, db: Session = Depends(get_db)):
    # Verify the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )
    return (
        db.query(OperatorLog)
        .filter(OperatorLog.user_id == user_id)
        .order_by(OperatorLog.created_at.desc())
        .all()
    )


# ── GET /api/operator-logs/{id} ─────────────────────────────────────────────

@router.get(
    "/{log_id}",
    response_model=OperatorLogRead,
    summary="Get a single log entry by ID",
    description="Returns one operator log entry. Returns 404 if not found.",
)
def get_operator_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(OperatorLog).filter(OperatorLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operator log with id={log_id} not found.",
        )
    return log


# ── POST /api/operator-logs ──────────────────────────────────────────────────

@router.post(
    "",
    response_model=OperatorLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Append a new audit log entry",
    description=(
        "Creates a new immutable audit log entry. "
        "user_id is optional (SET NULL on user deletion). "
        "action is required and should be a short action code "
        "such as 'APPROVE_RECOMMENDATION', 'CREATE_USER', 'ACTIVATE_EMERGENCY_ROUTE'. "
        "Note: PUT/DELETE are intentionally not implemented — "
        "operator logs are an append-only audit trail."
    ),
)
def create_operator_log(
    payload: OperatorLogCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Append a new log entry.

    Error cases:
    - 404: user_id does not exist (if provided)
    - 422: action is empty or exceeds 100 characters
    """
    # Validate user FK if provided
    if payload.user_id is not None:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={payload.user_id} not found. "
                       f"Cannot log action for a non-existent operator.",
            )

    new_log = OperatorLog(
        user_id=current_user.id,
        action=payload.action,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        description=payload.description,
    )

    try:
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create log entry — check constraint violations.",
        ) from exc

    return new_log

# ── No PUT / No DELETE ────────────────────────────────────────────────────────
# Operator logs are the audit trail of the system.
# They must never be altered or erased.
# PUT and DELETE are intentionally not implemented.
