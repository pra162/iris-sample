from __future__ import annotations

from uuid import uuid4

from geoalchemy2 import Geometry

from sqlalchemy import BigInteger
from sqlalchemy import Float
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.entity import BaseEntity


class Facility(BaseEntity):

    __tablename__ = "facilities"

    __table_args__ = (

        # --------------------------------------------------
        # Indexes
        # --------------------------------------------------

        Index(
            "idx_facility_source_id",
            "source_id",
        ),

        Index(
            "idx_facility_company",
            "company",
        ),

        Index(
            "idx_facility_city",
            "city",
        ),

        Index(
            "idx_facility_country",
            "country",
        ),

        Index(
            "idx_facility_geometry",
            "geometry",
            postgresql_using="gist",
        ),

        # --------------------------------------------------
        # External source identity
        #
        # Data Center Map ID uniquely identifies the
        # facility in the external source.
        # --------------------------------------------------

        UniqueConstraint(
            "source_id",
            name="uq_facility_source_id",
        ),

        {
            "schema": "iris_core",
        },
    )

    # ======================================================
    # INTERNAL ID
    # ======================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # ======================================================
    # SOURCE ID
    # ======================================================

    source_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # ======================================================
    # COUNTRY
    # ======================================================

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
    )

    # ======================================================
    # FACILITY INFORMATION
    # ======================================================

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
    )

    city: Mapped[str | None] = mapped_column(
        String(150),
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ======================================================
    # COORDINATES
    # ======================================================

    latitude: Mapped[float | None] = mapped_column(
        Float,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
    )

    # ======================================================
    # POSTGIS GEOMETRY
    # ======================================================

    geometry: Mapped[str | None] = mapped_column(
        Geometry(
            geometry_type="POINT",
            srid=4326,
            spatial_index=False,
        ),
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    news_matches: Mapped[list["NewsMatch"]] = relationship(
        "NewsMatch",
        back_populates="facility",
    )