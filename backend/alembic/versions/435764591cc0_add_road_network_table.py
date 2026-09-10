"""add_road_network_table

Revision ID: 435764591cc0
Revises: 3a994b110de2
Create Date: 2026-09-09 11:32:12.131099

PURPOSE:
    Adds the 'road_network' table to store Vadodara OpenStreetMap road segments.

SAFETY:
    - ONLY creates the new road_network table and its indexes.
    - Does NOT alter, drop, truncate, or touch any existing table.
    - Does NOT modify traffic_records, users, junctions, or any other table.
    - Is fully reversible: downgrade drops road_network only.

DATA SOURCE:
    OpenStreetMap contributors (ODbL License)
    Vadodara road network — 45,903 LineString road segments.

GEOMETRY:
    PostGIS is NOT installed. Geometry stored as JSONB (GeoJSON geometry object).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '435764591cc0'
down_revision: Union[str, Sequence[str], None] = '3a994b110de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add the road_network table.

    ONLY creates road_network — does NOT modify any existing table.
    """
    op.create_table(
        'road_network',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'osm_id',
            sa.String(length=30),
            nullable=False,
            comment="OpenStreetMap element ID, e.g. 'way/28812561'",
        ),
        sa.Column(
            'highway_type',
            sa.String(length=50),
            nullable=False,
            comment='OSM highway tag: primary, secondary, tertiary, residential, etc.',
        ),
        sa.Column(
            'road_name',
            sa.String(length=300),
            nullable=True,
            comment='English road name from OSM (present in ~2% of roads)',
        ),
        sa.Column(
            'ref',
            sa.String(length=50),
            nullable=True,
            comment="Road reference number, e.g. 'NH48'",
        ),
        sa.Column(
            'lanes',
            sa.Integer(),
            nullable=True,
            comment="Number of lanes (OSM 'lanes' tag, present in ~0.7% of roads)",
        ),
        sa.Column(
            'maxspeed',
            sa.Integer(),
            nullable=True,
            comment="Speed limit in km/h (OSM 'maxspeed' tag, present in ~0.6% of roads)",
        ),
        sa.Column(
            'oneway',
            sa.Boolean(),
            nullable=False,
            comment="True if the road is one-way (OSM 'oneway=yes')",
        ),
        sa.Column(
            'surface',
            sa.String(length=50),
            nullable=True,
            comment='Surface type: asphalt, unpaved, concrete, etc.',
        ),
        sa.Column(
            'bridge',
            sa.Boolean(),
            nullable=False,
            comment="True if OSM 'bridge=yes'",
        ),
        sa.Column(
            'tunnel',
            sa.Boolean(),
            nullable=False,
            comment="True if OSM 'tunnel=yes'",
        ),
        sa.Column(
            'road_length_m',
            sa.Float(),
            nullable=True,
            comment='Approximate road length in metres (haversine, calculated on import)',
        ),
        sa.Column(
            'geometry_json',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment='GeoJSON geometry object (type + coordinates). PostGIS not available — stored as JSONB.',
        ),
        sa.Column(
            'imported_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='Timestamp when this record was imported from the GeoJSON dataset',
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Indexes for road_network table only
    op.create_index('ix_road_network_id',           'road_network', ['id'],           unique=False)
    op.create_index('ix_road_network_osm_id',        'road_network', ['osm_id'],       unique=True)
    op.create_index('ix_road_network_highway_type',  'road_network', ['highway_type'], unique=False)
    op.create_index('ix_road_network_road_name',     'road_network', ['road_name'],    unique=False)


def downgrade() -> None:
    """
    Remove the road_network table.

    ONLY drops road_network — does NOT modify any other table.
    """
    op.drop_index('ix_road_network_road_name',    table_name='road_network')
    op.drop_index('ix_road_network_highway_type', table_name='road_network')
    op.drop_index('ix_road_network_osm_id',       table_name='road_network')
    op.drop_index('ix_road_network_id',           table_name='road_network')
    op.drop_table('road_network')
