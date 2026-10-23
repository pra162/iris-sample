from geoalchemy2 import Geometry
from sqlalchemy import Float
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.entity import BaseEntity


class LandValue(BaseEntity):
    """
    BORIS NRW land value polygons.
    """

    __tablename__ = "land_values"

    __table_args__ = (
        Index(
            "idx_land_value_municipality",
            "municipality",
        ),
        Index(
            "idx_land_value_postal_code",
            "postal_code",
        ),
        Index(
            "idx_land_value_country_code",
            "country_code",
        ),
        Index(
            "idx_land_value_geometry",
            "geometry",
            postgresql_using="gist",
        ),
        {
            "schema": "iris_core",
        },
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    municipality: Mapped[str | None] = mapped_column(
        String(150),
    )

    district: Mapped[str | None] = mapped_column(
        String(150),
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
    )

    land_value_eur_m2: Mapped[float | None] = mapped_column(
        Float,
    )

    geometry: Mapped[str] = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=25832,
            spatial_index=False,
        ),
        nullable=False,
    )