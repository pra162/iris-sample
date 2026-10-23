from geoalchemy2 import Geometry
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.entity import BaseEntity

from sqlalchemy import BigInteger

class PowerInfrastructure(BaseEntity):
    """
    OpenStreetMap power infrastructure.

    Includes:
        - Substations
        - Transformers
        - Power Lines
        - Towers
        - Poles
        - Cables
    """

    __tablename__ = "power_infrastructure"

    __table_args__ = (
        Index(
            "idx_power_infrastructure_osm_id",
            "osm_id",
        ),
        Index(
            "idx_power_infrastructure_power_type",
            "power_type",
        ),
        Index(
            "idx_power_infrastructure_geometry",
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
        index=True,
    )

    osm_id: Mapped[int] = mapped_column(
    BigInteger,
    nullable=False,
    unique=True,
    )

    element_type: Mapped[str | None] = mapped_column(
        String(20),
    )

    power_type: Mapped[str | None] = mapped_column(
        String(50),
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
    )

    operator: Mapped[str | None] = mapped_column(
        String(255),
    )

    voltage: Mapped[str | None] = mapped_column(
        String(100),
    )

    frequency: Mapped[str | None] = mapped_column(
        String(100),
    )

    reference: Mapped[str | None] = mapped_column(
        String(100),
    )

    geometry: Mapped[str] = mapped_column(
        Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )