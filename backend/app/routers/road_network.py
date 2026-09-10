"""
backend/app/routers/road_network.py
======================================
FastAPI endpoints for the Vadodara road network dataset.

Data source: OpenStreetMap contributors (ODbL License)
            https://www.openstreetmap.org/copyright

IMPORTANT:
    This API serves GEOGRAPHIC road network data ONLY.
    - Road geometry (LineString coordinates)
    - Road classification (highway type)
    - Road attributes (name, lanes, maxspeed, surface, etc.)

    It does NOT contain:
    - Traffic volume
    - Vehicle counts
    - Congestion levels
    - Real-time data of any kind

    Traffic data comes from the separate /api/traffic-records endpoint.

Endpoints:
    GET /api/road-network              → Paginated road list (summary, no geometry)
    GET /api/road-network/geojson      → GeoJSON FeatureCollection (with geometry)
    GET /api/road-network/stats        → Dataset statistics
    GET /api/road-network/{id}         → Single road detail (with geometry)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.road_network import RoadNetwork
from app.schemas.road_network import (
    RoadNetworkResponse,
    RoadNetworkSummary,
    RoadNetworkGeoJSONFeature,
    RoadNetworkGeoJSONCollection,
    RoadNetworkStats,
)

router = APIRouter(
    prefix="/api/road-network",
    tags=["Road Network (OpenStreetMap)"],
)


# ── GET /api/road-network/stats ───────────────────────────────────────────────
# NOTE: Must be defined BEFORE /{id} to avoid "stats" being matched as an ID.

@router.get(
    "/stats",
    response_model=RoadNetworkStats,
    summary="Road network dataset statistics",
    description=(
        "Returns aggregate statistics about the imported Vadodara road network.\n\n"
        "**Data source:** OpenStreetMap contributors (ODbL License)\n\n"
        "**Important:** This data contains geographic road attributes only — "
        "no traffic volume, vehicle counts, or congestion levels."
    ),
)
def get_road_network_stats(db: Session = Depends(get_db)):
    """Return statistics about the road_network dataset."""
    total = db.query(RoadNetwork).count()
    if total == 0:
        return RoadNetworkStats(
            total_roads=0,
            roads_with_names=0,
            one_way_roads=0,
            bridges=0,
            tunnels=0,
            highway_breakdown={},
        )

    roads_with_names = db.query(RoadNetwork).filter(
        RoadNetwork.road_name.isnot(None)
    ).count()

    one_way = db.query(RoadNetwork).filter(RoadNetwork.oneway == True).count()  # noqa: E712
    bridges = db.query(RoadNetwork).filter(RoadNetwork.bridge == True).count()  # noqa: E712
    tunnels = db.query(RoadNetwork).filter(RoadNetwork.tunnel == True).count()  # noqa: E712

    highway_rows = (
        db.query(RoadNetwork.highway_type, func.count(RoadNetwork.id))
        .group_by(RoadNetwork.highway_type)
        .order_by(func.count(RoadNetwork.id).desc())
        .all()
    )
    highway_breakdown = {row[0]: row[1] for row in highway_rows}

    return RoadNetworkStats(
        total_roads=total,
        roads_with_names=roads_with_names,
        one_way_roads=one_way,
        bridges=bridges,
        tunnels=tunnels,
        highway_breakdown=highway_breakdown,
    )


# ── GET /api/road-network/geojson ─────────────────────────────────────────────

@router.get(
    "/geojson",
    response_model=RoadNetworkGeoJSONCollection,
    summary="Road network as GeoJSON FeatureCollection",
    description=(
        "Returns road segments as a GeoJSON FeatureCollection, suitable for "
        "rendering on maps (Leaflet, MapLibre, SVG, etc.).\n\n"
        "**Default limit:** 500 features. Use `highway_type` filter to narrow results.\n\n"
        "**Data source:** OpenStreetMap contributors (ODbL License)\n\n"
        "**Attribution required:** 'Road network data © OpenStreetMap contributors'\n\n"
        "**Important:** Geographic data only — no traffic volume, congestion, or vehicle counts."
    ),
)
def get_road_network_geojson(
    highway_type: str | None = Query(
        None,
        description="Filter by highway type, e.g. 'primary', 'secondary', 'trunk', 'motorway'",
    ),
    oneway: bool | None = Query(None, description="Filter one-way roads only"),
    has_name: bool | None = Query(None, description="Filter roads that have a name"),
    limit: int = Query(500, ge=1, le=2000, description="Maximum features to return (max 2000)"),
    skip: int = Query(0, ge=0, description="Number of features to skip (offset)"),
    db: Session = Depends(get_db),
):
    """
    Returns road segments as GeoJSON FeatureCollection.

    Use highway_type filter to get major roads:
    - primary, secondary, trunk, motorway → major arterial roads
    - tertiary → secondary arterial roads
    - residential, service → local streets (large dataset)
    """
    q = db.query(RoadNetwork)

    if highway_type:
        q = q.filter(RoadNetwork.highway_type == highway_type)
    if oneway is not None:
        q = q.filter(RoadNetwork.oneway == oneway)
    if has_name is True:
        q = q.filter(RoadNetwork.road_name.isnot(None))
    elif has_name is False:
        q = q.filter(RoadNetwork.road_name.is_(None))

    roads = q.offset(skip).limit(limit).all()

    features = [RoadNetworkGeoJSONFeature.from_orm_row(r) for r in roads]

    return RoadNetworkGeoJSONCollection(
        type="FeatureCollection",
        total=len(features),
        features=features,
    )


# ── GET /api/road-network ─────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[RoadNetworkSummary],
    summary="List road segments (paginated, no geometry)",
    description=(
        "Returns a paginated list of road segments **without geometry** to keep responses small.\n\n"
        "Use `/api/road-network/geojson` to get geometry for map rendering.\n\n"
        "**Data source:** OpenStreetMap contributors (ODbL License)\n\n"
        "**Important:** Road attributes only — no traffic data."
    ),
)
def list_road_network(
    highway_type: str | None = Query(None, description="Filter by highway type"),
    road_name:    str | None = Query(None, description="Search road name (case-insensitive partial match)"),
    oneway:       bool | None = Query(None, description="Filter one-way roads"),
    limit:        int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    skip:         int = Query(0, ge=0, description="Offset for pagination"),
    db:           Session = Depends(get_db),
):
    q = db.query(RoadNetwork)

    if highway_type:
        q = q.filter(RoadNetwork.highway_type == highway_type)
    if road_name:
        q = q.filter(RoadNetwork.road_name.ilike(f"%{road_name}%"))
    if oneway is not None:
        q = q.filter(RoadNetwork.oneway == oneway)

    return q.offset(skip).limit(limit).all()


# ── GET /api/road-network/{id} ────────────────────────────────────────────────

@router.get(
    "/{road_id}",
    response_model=RoadNetworkResponse,
    summary="Get a single road segment by ID",
    description=(
        "Returns full road details including GeoJSON geometry.\n\n"
        "**Data source:** OpenStreetMap contributors (ODbL License)\n\n"
        "Returns 404 if the road ID does not exist."
    ),
)
def get_road_by_id(road_id: int, db: Session = Depends(get_db)):
    road = db.query(RoadNetwork).filter(RoadNetwork.id == road_id).first()
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road with id={road_id} not found in road_network table.",
        )
    return road
