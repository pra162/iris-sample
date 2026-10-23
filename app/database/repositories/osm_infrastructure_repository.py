from __future__ import annotations

from geoalchemy2 import Geography

from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.osm_infrastructure import (
    OsmInfrastructure,
)

from app.database.repositories.base_repository import (
    BaseRepository,
)


class OsmInfrastructureRepository(
    BaseRepository[OsmInfrastructure]
):
    """
    Repository for generic OpenStreetMap infrastructure.

    Supports:

        - Telecom lines
        - Fibre infrastructure
        - Communication towers
        - Communication masts
        - Exchanges
        - Connection points
        - Data centers
        - Other OSM infrastructure

    The repository is country-agnostic.

    Spatial data is stored in EPSG:4326.
    """

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            session,
            OsmInfrastructure,
        )

    # ======================================================
    # BASIC QUERIES
    # ======================================================

    def find_by_id(
        self,
        infrastructure_id: int,
    ) -> OsmInfrastructure | None:

        return self.session.get(
            OsmInfrastructure,
            infrastructure_id,
        )

    # ------------------------------------------------------

    def find_by_osm_id(
        self,
        osm_id: int,
        country_code: str | None = None,
    ) -> OsmInfrastructure | None:

        statement = (
            select(OsmInfrastructure)
            .where(
                OsmInfrastructure.osm_id == osm_id
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        return self.session.scalar(
            statement
        )

    # ------------------------------------------------------

    def find_by_infrastructure_type(
        self,
        infrastructure_type: str,
        country_code: str | None = None,
    ) -> list[OsmInfrastructure]:

        statement = (
            select(OsmInfrastructure)
            .where(
                OsmInfrastructure.infrastructure_type
                == infrastructure_type
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        statement = statement.order_by(
            OsmInfrastructure.name
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ------------------------------------------------------

    def count(
        self,
        country_code: str | None = None,
    ) -> int:

        statement = (
            select(
                func.count()
            )
            .select_from(
                OsmInfrastructure
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        return (
            self.session.scalar(
                statement
            )
            or 0
        )

    # ------------------------------------------------------

    def delete_all(
        self,
        country_code: str | None = None,
    ) -> None:

        query = self.session.query(
            OsmInfrastructure
        )

        if country_code:

            query = query.filter(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        query.delete(
            synchronize_session=False
        )

        self.session.commit()

    # ======================================================
    # MAP DATA
    # ======================================================

    def get_for_map(
        self,
        country_code: str | None = None,
    ):
        """
        Returns OSM infrastructure with:

            - metadata
            - centroid latitude
            - centroid longitude
            - GeoJSON geometry

        The original geometry is preserved.
        """

        statement = (
            select(
                OsmInfrastructure.id,
                OsmInfrastructure.osm_id,
                OsmInfrastructure.country_code,
                OsmInfrastructure.infrastructure_type,
                OsmInfrastructure.name,
                OsmInfrastructure.operator,
                OsmInfrastructure.element_type,
                OsmInfrastructure.reference,
                OsmInfrastructure.technology,
                OsmInfrastructure.medium,
                OsmInfrastructure.connection_type,
                OsmInfrastructure.capacity,

                func.ST_Y(
                    func.ST_Centroid(
                        OsmInfrastructure.geometry
                    )
                ).label(
                    "latitude"
                ),

                func.ST_X(
                    func.ST_Centroid(
                        OsmInfrastructure.geometry
                    )
                ).label(
                    "longitude"
                ),

                func.ST_AsGeoJSON(
                    OsmInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # TELECOM / FIBRE
    # ======================================================

    def get_telecom_infrastructure(
        self,
        country_code: str | None = None,
    ):
        """
        Returns telecom-related OSM infrastructure.

        The method intentionally keeps the source
        infrastructure categories instead of normalizing
        them so the original OSM classification remains
        available to the application.
        """

        telecom_types = [
            "telecom",
            "telecom_line",
            "communication_line",
            "fibre",
            "exchange",
            "connection_point",
            "telecom_utility",
            "communication_tower",
            "communications_tower",
            "communication_mast",
            "service_device",
            "data_center",
        ]

        statement = (
            select(
                OsmInfrastructure.id,
                OsmInfrastructure.osm_id,
                OsmInfrastructure.country_code,
                OsmInfrastructure.infrastructure_type,
                OsmInfrastructure.name,
                OsmInfrastructure.operator,
                OsmInfrastructure.reference,
                OsmInfrastructure.technology,
                OsmInfrastructure.medium,
                OsmInfrastructure.connection_type,
                OsmInfrastructure.capacity,

                func.ST_AsGeoJSON(
                    OsmInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
            .where(
                OsmInfrastructure.infrastructure_type.in_(
                    telecom_types
                )
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # NEAREST INFRASTRUCTURE
    # ======================================================

    def find_nearest(
        self,
        latitude: float,
        longitude: float,
        country_code: str | None = None,
        infrastructure_type: str | None = None,
    ):
        """
        Returns the nearest OSM infrastructure feature.

        Distance is returned in kilometres.
        """

        point = func.ST_SetSRID(
            func.ST_Point(
                longitude,
                latitude,
            ),
            4326,
        )

        distance = (
            func.ST_Distance(
                cast(
                    OsmInfrastructure.geometry,
                    Geography,
                ),
                cast(
                    point,
                    Geography,
                ),
            )
            / 1000
        ).label(
            "distance_km"
        )

        statement = (
            select(
                OsmInfrastructure.id,
                OsmInfrastructure.osm_id,
                OsmInfrastructure.country_code,
                OsmInfrastructure.infrastructure_type,
                OsmInfrastructure.name,
                OsmInfrastructure.operator,
                OsmInfrastructure.reference,
                OsmInfrastructure.technology,
                OsmInfrastructure.medium,
                distance,
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        if infrastructure_type:

            statement = statement.where(
                OsmInfrastructure.infrastructure_type
                == infrastructure_type
            )

        statement = (
            statement
            .order_by(distance)
            .limit(1)
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .first()
        )

    # ======================================================
    # NEARBY INFRASTRUCTURE
    # ======================================================

    def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        country_code: str | None = None,
        infrastructure_type: str | None = None,
    ):
        """
        Returns OSM infrastructure within a radius
        around a coordinate.

        Results include distance in kilometres and
        GeoJSON geometry.
        """

        point = func.ST_SetSRID(
            func.ST_Point(
                longitude,
                latitude,
            ),
            4326,
        )

        distance = (
            func.ST_Distance(
                cast(
                    OsmInfrastructure.geometry,
                    Geography,
                ),
                cast(
                    point,
                    Geography,
                ),
            )
            / 1000
        ).label(
            "distance_km"
        )

        statement = (
            select(
                OsmInfrastructure.id,
                OsmInfrastructure.osm_id,
                OsmInfrastructure.country_code,
                OsmInfrastructure.infrastructure_type,
                OsmInfrastructure.name,
                OsmInfrastructure.operator,
                OsmInfrastructure.reference,
                OsmInfrastructure.technology,
                OsmInfrastructure.medium,
                OsmInfrastructure.connection_type,
                OsmInfrastructure.capacity,

                distance,

                func.ST_AsGeoJSON(
                    OsmInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
            .where(
                distance <= radius_km
            )
        )

        if country_code:

            statement = statement.where(
                OsmInfrastructure.country_code
                == country_code.upper()
            )

        if infrastructure_type:

            statement = statement.where(
                OsmInfrastructure.infrastructure_type
                == infrastructure_type
            )

        statement = statement.order_by(
            distance
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )