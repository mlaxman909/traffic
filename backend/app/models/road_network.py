"""
backend/app/models/road_network.py
===================================
SQLAlchemy model for the 'road_network' table.

Stores Vadodara road segments imported from OpenStreetMap.

Data source: OpenStreetMap contributors (ODbL License)
Import date: 2026-09-09
Features:   45,903 LineString road segments

IMPORTANT:
- This table is INDEPENDENT of traffic_records and junctions.
- OSM data contains ONLY geographic/attribute data (no traffic volume).
- PostGIS is NOT installed on this server. Geometry is stored as JSONB.
- The geometry_json column stores the GeoJSON geometry object (type + coordinates).
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RoadNetwork(Base):
    """
    Represents a single road segment from the OpenStreetMap Vadodara dataset.
    Maps to the 'road_network' table in PostgreSQL.

    Geometry is stored as JSONB (GeoJSON geometry object) because PostGIS
    is not available. The API returns it in GeoJSON Feature format.
    """
    __tablename__ = "road_network"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ── OSM Identification ────────────────────────────────────────────────────

    # OSM element ID, e.g. "way/28812561" — unique per row
    osm_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        comment="OpenStreetMap element ID, e.g. 'way/28812561'"
    )

    # ── Road Classification ───────────────────────────────────────────────────

    # OSM 'highway' tag — always present (e.g. 'primary', 'residential')
    highway_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="OSM highway tag: primary, secondary, tertiary, residential, etc."
    )

    # ── Road Identity / Name (sparse — only ~2% of roads have names) ─────────

    # OSM 'name' tag — English name if present
    road_name: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
        comment="English road name from OSM (present in ~2% of roads)"
    )

    # OSM 'ref' tag — road reference number (e.g. NH48, SH87)
    ref: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Road reference number, e.g. 'NH48'"
    )

    # ── Traffic Characteristics ───────────────────────────────────────────────

    # OSM 'lanes' tag — number of traffic lanes
    lanes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of lanes (OSM 'lanes' tag, present in ~0.7% of roads)"
    )

    # OSM 'maxspeed' tag — speed limit in km/h
    maxspeed: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Speed limit in km/h (OSM 'maxspeed' tag, present in ~0.6% of roads)"
    )

    # OSM 'oneway' tag — True if one-way road
    oneway: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if the road is one-way (OSM 'oneway=yes')"
    )

    # ── Physical Characteristics ──────────────────────────────────────────────

    # OSM 'surface' tag — road surface material
    surface: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Surface type: asphalt, unpaved, concrete, etc."
    )

    # True if this road segment is a bridge
    bridge: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if OSM 'bridge=yes'"
    )

    # True if this road segment is a tunnel
    tunnel: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if OSM 'tunnel=yes'"
    )

    # ── Derived Attributes ────────────────────────────────────────────────────

    # Road segment length in metres (calculated from LineString coordinates)
    # Uses haversine formula — approximate, sufficient for display purposes
    road_length_m: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Approximate road length in metres (haversine, calculated on import)"
    )

    # ── Geometry ──────────────────────────────────────────────────────────────
    # PostGIS is NOT installed. Geometry stored as JSONB (GeoJSON geometry object).
    # Format: {"type": "LineString", "coordinates": [[lon, lat], ...]}
    # The API returns this wrapped in a GeoJSON Feature.

    geometry_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="GeoJSON geometry object (type + coordinates). PostGIS not available — stored as JSONB."
    )

    # ── Metadata ──────────────────────────────────────────────────────────────

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Timestamp when this record was imported from the GeoJSON dataset"
    )

    # ── Table-level Indexes ───────────────────────────────────────────────────

    __table_args__ = (
        Index("ix_road_network_highway_type", "highway_type"),
        Index("ix_road_network_osm_id", "osm_id", unique=True),
        Index("ix_road_network_road_name", "road_name"),
    )

    def __repr__(self) -> str:
        return (
            f"<RoadNetwork id={self.id} osm_id={self.osm_id!r} "
            f"highway={self.highway_type!r} name={self.road_name!r}>"
        )
