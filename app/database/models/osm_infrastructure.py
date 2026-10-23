from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class OsmInfrastructure(Base):
    """
    Generic OpenStreetMap infrastructure.

    Designed to support infrastructure from multiple
    countries without duplicating the database model.
    """

    __tablename__ = "osm_infrastructure"
    __table_args__ = (
        Index(
            "idx_osm_infrastructure_country_code",
            "country_code",
        ),
        Index(
            "idx_osm_infrastructure_osm_id",
            "osm_id",
        ),
        Index(
            "idx_osm_infrastructure_type",
            "infrastructure_type",
        ),
        Index(
            "idx_osm_infrastructure_geometry",
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
        autoincrement=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="osm",
    )

    osm_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    element_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    infrastructure_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    operator: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    technology: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    medium: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    connection_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    capacity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    geometry: Mapped[object] = mapped_column(
        Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )