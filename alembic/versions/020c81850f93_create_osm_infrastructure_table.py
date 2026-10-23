"""create osm infrastructure table

Revision ID: 020c81850f93
Revises: 7f2c1d8e4a91
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = "020c81850f93"
down_revision: Union[str, Sequence[str], None] = "7f2c1d8e4a91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the OSM infrastructure table."""

    op.create_table(
        "osm_infrastructure",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "country_code",
            sa.String(length=2),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=50),
            nullable=False,
            server_default="osm",
        ),

        sa.Column(
            "osm_id",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "element_type",
            sa.String(length=20),
            nullable=True,
        ),

        sa.Column(
            "infrastructure_type",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "operator",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "reference",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "technology",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "medium",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "connection_type",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "capacity",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "geometry",
            Geometry(
                geometry_type="GEOMETRY",
                srid=4326,
                spatial_index=False,
            ),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.PrimaryKeyConstraint("id"),

        schema="iris_core",
    )

    # -------------------------------------------------
    # Indexes
    # -------------------------------------------------

    op.create_index(
        "idx_osm_infrastructure_country_code",
        "osm_infrastructure",
        ["country_code"],
        unique=False,
        schema="iris_core",
    )

    op.create_index(
        "idx_osm_infrastructure_osm_id",
        "osm_infrastructure",
        ["osm_id"],
        unique=False,
        schema="iris_core",
    )

    op.create_index(
        "idx_osm_infrastructure_type",
        "osm_infrastructure",
        ["infrastructure_type"],
        unique=False,
        schema="iris_core",
    )

    op.create_index(
        "idx_osm_infrastructure_geometry",
        "osm_infrastructure",
        ["geometry"],
        unique=False,
        schema="iris_core",
        postgresql_using="gist",
    )


def downgrade() -> None:
    """Drop the OSM infrastructure table."""

    op.drop_index(
        "idx_osm_infrastructure_geometry",
        table_name="osm_infrastructure",
        schema="iris_core",
    )

    op.drop_index(
        "idx_osm_infrastructure_type",
        table_name="osm_infrastructure",
        schema="iris_core",
    )

    op.drop_index(
        "idx_osm_infrastructure_osm_id",
        table_name="osm_infrastructure",
        schema="iris_core",
    )

    op.drop_index(
        "idx_osm_infrastructure_country_code",
        table_name="osm_infrastructure",
        schema="iris_core",
    )

    op.drop_table(
        "osm_infrastructure",
        schema="iris_core",
    )