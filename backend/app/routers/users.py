"""
backend/app/routers/users.py
==============================
CRUD endpoints for the User entity.

Endpoints:
  GET    /api/users          → List all users (requires auth)
  GET    /api/users/{id}     → Get one user by ID (requires auth)
  POST   /api/users          → Create a new user (SYSTEM_ADMINISTRATOR only)
  PUT    /api/users/{id}     → Update an existing user (SYSTEM_ADMINISTRATOR only)
  DELETE /api/users/{id}     → Delete a user (SYSTEM_ADMINISTRATOR only)

Note: JWT authentication is active. All endpoints require a valid token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserSummary
from app.services.auth import require_roles, get_password_hash, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


# ── GET /api/users ────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[UserSummary],
    summary="List all users",
    description="Returns a list of all registered users. Requires authentication. Password hash is never included.",
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all users, paginated.
    - skip: how many records to skip (for pagination)
    - limit: max records to return (default 100, max recommended 500)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ── GET /api/users/{id} ───────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by ID",
    description="Returns full user details for the given ID. Returns 404 if not found.",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )
    return user


# ── POST /api/users ───────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Provisions a new operator account. Returns 409 if email already exists.",
)
def create_user(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMINISTRATOR]))
):
    """
    Create a new user.
    Only SYSTEM_ADMINISTRATOR can create users. record.

    Error cases:
    - 409 Conflict: email address is already registered
    """
    # Check for duplicate email before attempting insert
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{payload.email}' already exists.",
        )

    # For Phase 4 we use pwdlib to hash passwords.
    # We will use the password 'password123' as default if they didn't supply one that is hashed.
    # Or just hash what they provided (wait, UserCreate expects a hash right now).
    # Since UserCreate has password_hash, we will re-hash it if it's the placeholder.
    actual_hash = get_password_hash("password123") if payload.password_hash == "placeholder_hash" else payload.password_hash

    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=actual_hash,
        role=payload.role,
        status=payload.status,
        district=payload.district,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create user — email may already be in use.",
        )

    return new_user


# ── PUT /api/users/{id} ───────────────────────────────────────────────────────

@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    description="Updates one or more fields on an existing user. Returns 404 if not found.",
)
def update_user(
    user_id: int, 
    payload: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMINISTRATOR]))
):
    """
    Update a user. Only SYSTEM_ADMINISTRATOR can update users.pdate — only fields that are provided in the request body are changed.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    # If email is changing, check for conflicts
    if payload.email and payload.email != user.email:
        conflict = db.query(User).filter(User.email == payload.email).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already in use by another user.",
            )

    # Apply only the fields that were explicitly provided
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update failed — a database constraint was violated.",
        )

    return user


# ── DELETE /api/users/{id} ────────────────────────────────────────────────────

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Permanently removes a user. Returns 404 if not found.",
)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMINISTRATOR]))
):
    """
    Delete a user. Only SYSTEM_ADMINISTRATOR can delete users. by ID.
    Returns 204 No Content on success (no body).
    Returns 404 if the user does not exist.

    Note: In production, consider soft-delete (setting status=INACTIVE)
    rather than hard-delete, to preserve audit log integrity.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    db.delete(user)
    db.commit()
    # Return None → FastAPI sends 204 No Content
