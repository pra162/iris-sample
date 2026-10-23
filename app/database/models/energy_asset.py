from sqlalchemy import Float
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from geoalchemy2 import Geometry

from app.database.entity import BaseEntity


class EnergyAsset(BaseEntity):

    __tablename__ = "energy_assets"

    __table_args__ = (
        Index(
            "idx_energy_asset_geometry",
            "geometry",
            postgresql_using="gist",
        ),
        Index(
            "idx_energy_asset_operator",
            "operator_name",
        ),
        Index(
            "idx_energy_asset_city",
            "city",
        ),
        Index(
            "idx_energy_asset_energy_type",
            "energy_type",
        ),
        UniqueConstraint(
            "mastr_number",
            name="uq_energy_asset_mastr_number",
        ),
        {
            "schema": "iris_core",
        },
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
    )

    mastr_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    location_id: Mapped[int | None] = mapped_column(
        Integer,
        index=True,
    )

    operator_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    operator_mastr_number: Mapped[str | None] = mapped_column(
        String(50),
    )

    city: Mapped[str | None] = mapped_column(
        String(150),
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
    )

    energy_type: Mapped[str | None] = mapped_column(
        String(150),
    )

    gross_power_kw: Mapped[float | None] = mapped_column(
        Float,
    )

    net_power_kw: Mapped[float | None] = mapped_column(
        Float,
    )

    status: Mapped[str | None] = mapped_column(
        String(100),
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
    )

    geometry: Mapped[str | None] = mapped_column(
    Geometry(
            geometry_type="POINT",
            srid=4326,
            spatial_index=False,
        )
    )