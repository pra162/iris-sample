from __future__ import annotations

import json
import logging
from pathlib import Path

from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from app.database.models.osm_infrastructure import (
    OsmInfrastructure,
)


logger = logging.getLogger(__name__)


class OsmInfrastructureParser:
    """
    Parses processed OSM infrastructure GeoJSON into
    OsmInfrastructure entities.
    """

    def parse(
        self,
        file_path: str | Path,
        country_code: str = "DE",
    ) -> list[OsmInfrastructure]:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        country_code = country_code.upper()

        logger.info(
            "Reading OSM infrastructure dataset..."
        )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        features = data.get(
            "features",
            [],
        )

        infrastructure: list[
            OsmInfrastructure
        ] = []

        skipped = 0

        for feature in features:

            entity = self._build_entity(
                feature,
                country_code,
            )

            if entity is None:
                skipped += 1
                continue

            infrastructure.append(entity)

        logger.info(
            "Parsed %s OSM infrastructure "
            "features (%s skipped).",
            len(infrastructure),
            skipped,
        )

        return infrastructure

    def _build_entity(
        self,
        feature: dict,
        country_code: str,
    ) -> OsmInfrastructure | None:

        properties = feature.get(
            "properties",
            {},
        )

        geometry_data = feature.get(
            "geometry"
        )

        osm_id = properties.get(
            "osm_id"
        )

        if osm_id is None:
            return None

        if not geometry_data:
            return None

        geometry = shape(
            geometry_data
        )

        infrastructure_type = (
            properties.get(
                "telecom_category"
            )
            or properties.get(
                "telecom_type"
            )
            or "telecom"
        )

        return OsmInfrastructure(
            country_code=country_code,

            source=properties.get(
                "source",
                "osm",
            ),

            osm_id=osm_id,

            element_type=properties.get(
                "element_type"
            ),

            infrastructure_type=(
                infrastructure_type
            ),

            name=properties.get(
                "name"
            ),

            operator=properties.get(
                "operator"
            ),

            reference=properties.get(
                "reference"
            ),

            technology=properties.get(
                "technology"
            ),

            medium=properties.get(
                "medium"
            ),

            connection_type=properties.get(
                "connection_type"
            ),

            capacity=properties.get(
                "capacity"
            ),

            geometry=from_shape(
                geometry,
                srid=4326,
            ),
        )