from __future__ import annotations

from geoalchemy2 import Geography

from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.power_infrastructure import (
    PowerInfrastructure,
)

from app.database.repositories.base_repository import (
    BaseRepository,
)


class PowerInfrastructureRepository(
    BaseRepository[PowerInfrastructure]
):
    """
    Repository for OpenStreetMap power infrastructure.

    Handles:

        - Substations
        - High-voltage transmission lines
        - Transformers
        - General power infrastructure
        - Spatial nearest-neighbour queries

    Spatial data is stored in EPSG:4326.

    Map methods return GeoJSON geometry so that the
    Streamlit dashboard and static map renderer can
    consume the infrastructure directly.
    """

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            session,
            PowerInfrastructure,
        )

    # ======================================================
    # BASIC QUERIES
    # ======================================================

    def find_by_id(
        self,
        infrastructure_id: int,
    ) -> PowerInfrastructure | None:

        return self.session.get(
            PowerInfrastructure,
            infrastructure_id,
        )

    # ------------------------------------------------------

    def find_by_osm_id(
        self,
        osm_id: int,
    ) -> PowerInfrastructure | None:

        statement = (
            select(PowerInfrastructure)
            .where(
                PowerInfrastructure.osm_id == osm_id
            )
        )

        return self.session.scalar(
            statement
        )

    # ------------------------------------------------------

    def find_by_power_type(
        self,
        power_type: str,
    ) -> list[PowerInfrastructure]:

        statement = (
            select(PowerInfrastructure)
            .where(
                PowerInfrastructure.power_type
                == power_type
            )
            .order_by(
                PowerInfrastructure.name
            )
        )

        return list(
            self.session.scalars(
                statement
            )
        )

    # ------------------------------------------------------

    def count(self) -> int:

        statement = (
            select(func.count())
            .select_from(
                PowerInfrastructure
            )
        )

        return (
            self.session.scalar(
                statement
            )
            or 0
        )

    # ------------------------------------------------------

    def delete_all(self) -> None:

        self.session.query(
            PowerInfrastructure
        ).delete()

        self.session.commit()

    # ======================================================
    # POWER INFRASTRUCTURE MAP
    # ======================================================

    def get_for_map(self):
        """
        Returns all power infrastructure with:

            - metadata
            - centroid latitude
            - centroid longitude
            - GeoJSON geometry

        Geometry is returned as a GeoJSON string.
        """

        statement = (
            select(
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.power_type,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                PowerInfrastructure.element_type,

                func.ST_Y(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "latitude"
                ),

                func.ST_X(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "longitude"
                ),

                func.ST_AsGeoJSON(
                    PowerInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # HIGH VOLTAGE SUBSTATIONS
    # ======================================================

    def get_high_voltage_substations(
        self,
    ):
        """
        Returns strategic 110/220/380kV substations.

        IMPORTANT:

        The geometry is explicitly returned as GeoJSON
        because the map renderer requires the actual
        geometry to draw the substation.

        Substations may be:

            - Point
            - Polygon
            - MultiPolygon

        The original geometry is preserved.
        """

        statement = (
            select(
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                PowerInfrastructure.element_type,

                func.ST_Y(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "latitude"
                ),

                func.ST_X(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "longitude"
                ),

                func.ST_AsGeoJSON(
                    PowerInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
            .where(
                PowerInfrastructure.power_type
                == "substation"
            )
            .where(
                or_(
                    PowerInfrastructure.voltage.like(
                        "%110000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%220000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%380000%"
                    ),
                )
            )
            .order_by(
                PowerInfrastructure.voltage.desc()
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # HIGH VOLTAGE TRANSMISSION LINES
    # ======================================================

    def get_high_voltage_lines(
        self,
    ):
        """
        Returns all strategic 110/220/380kV transmission
        lines as GeoJSON.

        IMPORTANT:

        No global LIMIT is applied here.

        The map renderer is responsible for filtering
        the lines geographically around the selected
        facility.

        Applying .limit(300) here would select only
        300 lines from the entire database before the
        geographic filtering happens. This can cause
        valid transmission lines near the selected site
        to be missing from the map.

        The original geometry is returned so the renderer
        can draw the actual transmission line.
        """

        statement = (
            select(
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,

                func.ST_AsGeoJSON(
                    PowerInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
            .where(
                PowerInfrastructure.power_type
                == "line"
            )
            .where(
                or_(
                    PowerInfrastructure.voltage.like(
                        "%110000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%220000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%380000%"
                    ),
                )
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # STRATEGIC TRANSFORMERS
    # ======================================================

    def get_strategic_transformers(
        self,
    ):
        """
        Returns strategic transformers.

        Geometry is explicitly returned as GeoJSON.

        Transformer selection includes:

            - 110kV
            - 150kV
            - 220kV
            - 380kV

        and strategic grid operators.
        """

        statement = (
            select(
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                PowerInfrastructure.element_type,

                func.ST_Y(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "latitude"
                ),

                func.ST_X(
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    )
                ).label(
                    "longitude"
                ),

                func.ST_AsGeoJSON(
                    PowerInfrastructure.geometry
                ).label(
                    "geometry"
                ),
            )
            .where(
                PowerInfrastructure.power_type
                == "transformer"
            )
            .where(
                or_(
                    PowerInfrastructure.voltage.like(
                        "%110000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%150000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%220000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%380000%"
                    ),

                    PowerInfrastructure.operator.in_(
                        [
                            "Amprion",
                            "Amprion GmbH",
                            "TenneT",
                            "Westnetz",
                            "RWE",
                            "DB Energie",
                            "DB Energie GmbH",
                            "Uniper Kraftwerke GmbH",
                        ]
                    ),
                )
            )
            .order_by(
                PowerInfrastructure.operator
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .all()
        )

    # ======================================================
    # NEAREST SUBSTATION
    # ======================================================

    def find_nearest_substation(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Returns the nearest strategic substation.
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
                    func.ST_Centroid(
                        PowerInfrastructure.geometry
                    ),
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
                PowerInfrastructure.id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                distance,
            )
            .where(
                PowerInfrastructure.power_type
                == "substation"
            )
            .order_by(
                distance
            )
            .limit(
                1
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .first()
        )

    # ======================================================
    # NEAREST HIGH VOLTAGE LINE
    # ======================================================

    def find_nearest_high_voltage_line(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Returns the nearest high-voltage transmission
        line.
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
                    PowerInfrastructure.geometry,
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
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                distance,
            )
            .where(
                PowerInfrastructure.power_type
                == "line"
            )
            .where(
                or_(
                    PowerInfrastructure.voltage.like(
                        "%110000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%220000%"
                    ),
                    PowerInfrastructure.voltage.like(
                        "%380000%"
                    ),
                )
            )
            .order_by(
                distance
            )
            .limit(
                1
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .first()
        )

    # ======================================================
    # NEAREST TRANSFORMER
    # ======================================================

    def find_nearest_transformer(
        self,
        latitude: float,
        longitude: float,
    ):
        """
        Returns the nearest strategic transformer.
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
                    PowerInfrastructure.geometry,
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
                PowerInfrastructure.id,
                PowerInfrastructure.osm_id,
                PowerInfrastructure.name,
                PowerInfrastructure.operator,
                PowerInfrastructure.voltage,
                distance,
            )
            .where(
                PowerInfrastructure.power_type
                == "transformer"
            )
            .order_by(
                distance
            )
            .limit(
                1
            )
        )

        return (
            self.session.execute(
                statement
            )
            .mappings()
            .first()
        )