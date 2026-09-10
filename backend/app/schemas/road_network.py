"""
backend/app/schemas/road_network.py
=====================================
Pydantic schemas for the RoadNetwork entity.

Data source: OpenStreetMap contributors (ODbL License)
Important: This is geographic road-network data ONLY.
           It does NOT contain traffic volume, congestion, or vehicle counts.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


# ── Base Schema ───────────────────────────────────────────────────────────────

class RoadNetworkBase(BaseModel):
    """Shared fields for RoadNetwork read schemas."""

    osm_id:       str  = Field(..., description="OpenStreetMap element ID, e.g. 'way/28812561'")
    highway_type: str  = Field(..., description="OSM highway classification: primary, secondary, residential, etc.")
    road_name:    str | None = Field(None, description="English road name (present in ~2% of roads)")
    ref:          str | None = Field(None, description="Road reference number, e.g. NH48")
    lanes:        int | None = Field(None, description="Number of traffic lanes")
    maxspeed:     int | None = Field(None, description="Speed limit in km/h")
    oneway:       bool       = Field(False, description="True if the road is one-way")
    surface:      str | None = Field(None, description="Road surface: asphalt, unpaved, concrete, etc.")
    bridge:       bool       = Field(False, description="True if this segment is a bridge")
    tunnel:       bool       = Field(False, description="True if this segment runs through a tunnel")
    road_length_m: float | None = Field(None, description="Approximate road length in metres")


# ── Response Schema ───────────────────────────────────────────────────────────

class RoadNetworkResponse(RoadNetworkBase):
    """
    Full road record returned by GET /api/road-network/{id}.
    Includes the GeoJSON geometry object.
    """
    model_config = ConfigDict(from_attributes=True)

    id:           int
    geometry_json: Any  = Field(
        ...,
        description=(
            "GeoJSON geometry object: {type: 'LineString', coordinates: [[lon, lat], ...]}\n"
            "Stored as JSONB (PostGIS not available).\n"
            "Data source: OpenStreetMap — geographic data only, no traffic volume."
        ),
    )
    imported_at:  datetime


# ── Summary Schema (no geometry — for list views) ─────────────────────────────

class RoadNetworkSummary(BaseModel):
    """
    Compact road record for paginated list endpoints.
    Omits the geometry to reduce payload size.
    """
    model_config = ConfigDict(from_attributes=True)

    id:           int
    osm_id:       str
    highway_type: str
    road_name:    str | None
    ref:          str | None
    lanes:        int | None
    maxspeed:     int | None
    oneway:       bool
    surface:      str | None
    bridge:       bool
    tunnel:       bool
    road_length_m: float | None


# ── GeoJSON Feature Schema ────────────────────────────────────────────────────

class RoadNetworkGeoJSONProperties(BaseModel):
    """Properties object inside a GeoJSON Feature."""
    model_config = ConfigDict(from_attributes=True)

    id:           int
    osm_id:       str
    highway_type: str
    road_name:    str | None
    ref:          str | None
    lanes:        int | None
    maxspeed:     int | None
    oneway:       bool
    surface:      str | None
    bridge:       bool
    tunnel:       bool
    road_length_m: float | None


class RoadNetworkGeoJSONFeature(BaseModel):
    """
    A single road segment formatted as a GeoJSON Feature.
    Compatible with Leaflet, MapLibre, and browser GeoJSON rendering.
    """
    type:       str = "Feature"
    id:         int
    geometry:   Any   # GeoJSON geometry object from geometry_json column
    properties: RoadNetworkGeoJSONProperties

    @classmethod
    def from_orm_row(cls, road) -> "RoadNetworkGeoJSONFeature":
        """Convert a RoadNetwork ORM object to a GeoJSON Feature."""
        return cls(
            type="Feature",
            id=road.id,
            geometry=road.geometry_json,
            properties=RoadNetworkGeoJSONProperties.model_validate(road),
        )


class RoadNetworkGeoJSONCollection(BaseModel):
    """
    A GeoJSON FeatureCollection of road segments.

    IMPORTANT ATTRIBUTION:
    Road network data © OpenStreetMap contributors (ODbL License).
    This dataset contains ONLY geographic road geometry and attributes.
    It does NOT provide traffic volume, congestion, or vehicle counts.

    Source: https://www.openstreetmap.org
    """
    type:        str  = "FeatureCollection"
    total:       int  = Field(..., description="Total features in this response")
    attribution: str  = Field(
        default="Road network data © OpenStreetMap contributors (ODbL). Geographic data only — no traffic volume.",
        description="Required OSM attribution",
    )
    features:    list[RoadNetworkGeoJSONFeature]


# ── Stats Schema ──────────────────────────────────────────────────────────────

class RoadNetworkStats(BaseModel):
    """
    Summary statistics for the road_network dataset.
    Returned by GET /api/road-network/stats.
    """
    total_roads:       int
    roads_with_names:  int
    one_way_roads:     int
    bridges:           int
    tunnels:           int
    highway_breakdown: dict[str, int]
    data_source:       str = "OpenStreetMap contributors (ODbL License)"
    attribution_note:  str = (
        "Road network data contains geographic attributes only. "
        "OSM does NOT provide live traffic data, vehicle counts, or congestion levels."
    )
