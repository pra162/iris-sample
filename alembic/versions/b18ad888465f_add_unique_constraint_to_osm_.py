"""add unique constraint to osm infrastructure

Revision ID: b18ad888465f
Revises: 020c81850f93
Create Date: 2026-08-20 14:49:35
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b18ad888465f"

down_revision: Union[str, Sequence[str], None] = (
    "020c81850f93"
)

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_unique_constraint(
        "uq_osm_infrastructure_country_source_osm",
        "osm_infrastructure",
        [
            "country_code",
            "source",
            "osm_id",
        ],
        schema="iris_core",
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_osm_infrastructure_country_source_osm",
        "osm_infrastructure",
        schema="iris_core",
        type_="unique",
    )