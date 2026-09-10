"""
backend/app/routers/traffic_records.py
========================================
CRUD endpoints for the TrafficRecord entity.

Endpoints:
  GET    /api/traffic-records                       → List records (paginated, filterable)
  GET    /api/traffic-records/summary               → Aggregated stats per junction
  GET    /api/traffic-records/junction/{jid}        → Records for one junction
  GET    /api/traffic-records/{id}                  → Get single record by ID
  POST   /api/traffic-records                       → Create a single test/manual record
  DELETE /api/traffic-records/{id}                  → Delete a single record by ID

DATASET PROTECTION:
  The 23,048 imported records are protected by design:
  - POST creates a single identifiable record (not bulk).
  - DELETE only removes the specific ID given.
  - There is NO bulk-delete or truncate endpoint.
  - The imported records (IDs 9–23,048+) are not touched by normal testing.
  Use clearly labelled test records for write-operation verification.

Note: Traffic records are primarily read-only — records are imported via
      the ETL script. POST/DELETE are provided for CRUD completeness only.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.traffic_record import TrafficRecord, TrafficLevel
from app.models.junction import Junction
from app.models.user import User
from app.schemas.traffic_record import TrafficRecordCreate, TrafficRecordRead
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/traffic-records", tags=["Traffic Records"])


# ── GET /api/traffic-records ─────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[TrafficRecordRead],
    summary="List traffic records",
    description=(
        "Returns paginated traffic records from PostgreSQL. "
        "Filter by junction_id, traffic_level, or date range. "
        "Records are ordered by recorded_at descending (most recent first)."
    ),
)
def list_traffic_records(
    skip:            int                  = Query(default=0,   ge=0,   description="Records to skip (pagination)"),
    limit:           int                  = Query(default=100, ge=1, le=1000, description="Max records to return"),
    junction_id:     int | None           = Query(default=None, description="Filter by junction DB id"),
    traffic_level:   TrafficLevel | None  = Query(default=None, description="Filter: LOW, MODERATE, HIGH, CRITICAL"),
    from_date:       datetime | None      = Query(default=None, description="Filter: recorded_at >= this datetime"),
    to_date:         datetime | None      = Query(default=None, description="Filter: recorded_at <= this datetime"),
    db: Session = Depends(get_db),
):
    """
    Returns traffic records with optional filtering.

    Examples:
    - All records: GET /api/traffic-records?limit=50
    - Junction 1 only: GET /api/traffic-records?junction_id=1&limit=100
    - HIGH traffic: GET /api/traffic-records?traffic_level=HIGH
    - Date range: GET /api/traffic-records?from_date=2024-01-15&to_date=2024-01-16
    """
    query = db.query(TrafficRecord)

    if junction_id is not None:
        query = query.filter(TrafficRecord.junction_id == junction_id)
    if traffic_level is not None:
        query = query.filter(TrafficRecord.traffic_level == traffic_level)
    if from_date is not None:
        query = query.filter(TrafficRecord.recorded_at >= from_date)
    if to_date is not None:
        query = query.filter(TrafficRecord.recorded_at <= to_date)

    records = (
        query
        .order_by(TrafficRecord.recorded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return records


# ── GET /api/traffic-records/summary ────────────────────────────────────────

@router.get(
    "/summary",
    summary="Aggregated traffic summary per junction",
    description="Returns count, avg congestion, and min/max vehicles per junction.",
    response_model=list[dict],
)
def traffic_summary(db: Session = Depends(get_db)):
    """
    Aggregated statistics — useful for dashboard KPI cards.
    Returns one row per junction with counts and averages.
    """
    rows = db.execute(
        __import__("sqlalchemy").text("""
            SELECT
                j.junction_code,
                j.name AS junction_name,
                COUNT(tr.id)                            AS total_records,
                ROUND(AVG(tr.congestion_percentage), 1) AS avg_congestion,
                MIN(tr.vehicles)                        AS min_vehicles,
                MAX(tr.vehicles)                        AS max_vehicles,
                COUNT(*) FILTER (WHERE tr.traffic_level = 'HIGH')     AS high_count,
                COUNT(*) FILTER (WHERE tr.traffic_level = 'CRITICAL') AS critical_count,
                MIN(tr.recorded_at)                     AS earliest_record,
                MAX(tr.recorded_at)                     AS latest_record
            FROM junctions j
            LEFT JOIN traffic_records tr ON tr.junction_id = j.id
            GROUP BY j.id, j.junction_code, j.name
            ORDER BY j.junction_code
        """)
    ).fetchall()

    return [
        {
            "junction_code":   r[0],
            "junction_name":   r[1],
            "total_records":   r[2],
            "avg_congestion":  float(r[3]) if r[3] is not None else None,
            "min_vehicles":    r[4],
            "max_vehicles":    r[5],
            "high_count":      r[6],
            "critical_count":  r[7],
            "earliest_record": str(r[8]) if r[8] else None,
            "latest_record":   str(r[9]) if r[9] else None,
        }
        for r in rows
    ]


# ── GET /api/traffic-records/{id} ────────────────────────────────────────────

@router.get(
    "/{record_id}",
    response_model=TrafficRecordRead,
    summary="Get single traffic record by ID",
    description="Returns one traffic record. Returns 404 if not found.",
)
def get_traffic_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(TrafficRecord).filter(TrafficRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traffic record with id={record_id} not found.",
        )
    return record


# ── POST /api/traffic-records ────────────────────────────────────────────────
# CRUD completeness endpoint.
# Use this for test records only — the 23,048 imported records must not be disturbed.

@router.post(
    "",
    response_model=TrafficRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single traffic record (CRUD test / manual entry)",
    description=(
        "Creates one traffic record in the database. "
        "junction_id must reference an existing junction. "
        "This endpoint exists for CRUD completeness. "
        "The 23,048 imported records are unaffected — "
        "use a clearly identified test record and delete it after testing."
    ),
)
def create_traffic_record(
    payload: TrafficRecordCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Error cases:
    - 404: junction_id does not exist
    - 422: vehicles < 0 or congestion_percentage out of 0–100 range
    """
    # Validate junction FK
    junction = db.query(Junction).filter(Junction.id == payload.junction_id).first()
    if not junction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction with id={payload.junction_id} not found. "
                   f"Cannot create a traffic record for a non-existent junction.",
        )

    recorded_at = payload.recorded_at if payload.recorded_at else datetime.now(timezone.utc)

    new_record = TrafficRecord(
        junction_id=payload.junction_id,
        recorded_at=recorded_at,
        vehicles=payload.vehicles,
        traffic_level=payload.traffic_level,
        congestion_percentage=payload.congestion_percentage,
    )

    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create traffic record — check constraint violations.",
        ) from exc

    return new_record


# ── DELETE /api/traffic-records/{id} ────────────────────────────────────────
# Removes ONE specific record by primary key.
# No bulk delete, no truncate — the imported dataset is protected.

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a single traffic record by ID",
    description=(
        "Permanently removes one traffic record. Returns 404 if not found. "
        "Use this to clean up test records created via POST. "
        "The 23,048 imported records are only affected if their specific ID is given."
    ),
)
def delete_traffic_record(
    record_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(TrafficRecord).filter(TrafficRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traffic record with id={record_id} not found.",
        )
    db.delete(record)
    db.commit()
