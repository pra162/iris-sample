"""add facility source id

Revision ID: 7f2c1d8e4a91
Revises: 13108b59b03f
Create Date: 2026-08-18
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f2c1d8e4a91"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "13108b59b03f"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:

    op.add_column(
        "facilities",
        sa.Column(
            "source_id",
            sa.BigInteger(),
            nullable=True,
        ),
        schema="iris_core",
    )

    op.drop_constraint(
        "uq_facility_company_name",
        "facilities",
        schema="iris_core",
        type_="unique",
    )

    op.create_index(
        "idx_facility_source_id",
        "facilities",
        ["source_id"],
        unique=False,
        schema="iris_core",
    )

    op.create_unique_constraint(
        "uq_facility_source_id",
        "facilities",
        ["source_id"],
        schema="iris_core",
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_facility_source_id",
        "facilities",
        schema="iris_core",
        type_="unique",
    )

    op.drop_index(
        "idx_facility_source_id",
        table_name="facilities",
        schema="iris_core",
    )

    op.create_unique_constraint(
        "uq_facility_company_name",
        "facilities",
        ["company", "name"],
        schema="iris_core",
    )

    op.drop_column(
        "facilities",
        "source_id",
        schema="iris_core",
    )