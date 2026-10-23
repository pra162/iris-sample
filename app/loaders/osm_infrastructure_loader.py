from __future__ import annotations

from pathlib import Path
import logging
import time

from sqlalchemy.orm import Session

from app.database.repositories.osm_infrastructure_repository import (
    OsmInfrastructureRepository,
)
from app.parsers.osm_infrastructure_parser import (
    OsmInfrastructureParser,
)


logger = logging.getLogger(__name__)


class OsmInfrastructureLoader:
    """
    Loads processed OSM infrastructure data into PostgreSQL/PostGIS.

    Pipeline:

        GeoJSON
            ↓
        OsmInfrastructureParser
            ↓
        OsmInfrastructure entities
            ↓
        OsmInfrastructureRepository
            ↓
        iris_core.osm_infrastructure
    """

    def __init__(
        self,
        session: Session,
    ):

        self.repository = (
            OsmInfrastructureRepository(
                session
            )
        )

        self.parser = (
            OsmInfrastructureParser()
        )

    def load(
        self,
        file_path: str | Path,
        country_code: str = "DE",
    ) -> dict:

        start_time = time.perf_counter()

        country_code = country_code.upper()

        logger.info(
            "Reading OSM infrastructure file..."
        )

        infrastructure = self.parser.parse(
            file_path,
            country_code=country_code,
        )

        logger.info(
            "Parsed %s OSM infrastructure features.",
            len(infrastructure),
        )

        # --------------------------------------------------
        # Remove duplicates inside the import file
        # --------------------------------------------------

        unique_infrastructure = []

        seen = set()

        for item in infrastructure:

            key = (
                item.country_code,
                item.source,
                item.osm_id,
            )

            if key in seen:
                continue

            seen.add(key)

            unique_infrastructure.append(
                item
            )

        duplicates_removed = (
            len(infrastructure)
            - len(unique_infrastructure)
        )

        logger.info(
            "Removed %s duplicate records.",
            duplicates_removed,
        )

        # --------------------------------------------------
        # Insert new records / update existing records
        # --------------------------------------------------

        inserted = 0
        updated = 0

        for item in unique_infrastructure:

            existing = (
                self.repository.find_by_osm_id(
                    item.osm_id,
                    country_code=country_code,
                )
            )

            if existing:

                existing.source = item.source
                existing.element_type = (
                    item.element_type
                )
                existing.infrastructure_type = (
                    item.infrastructure_type
                )
                existing.name = item.name
                existing.operator = item.operator
                existing.reference = (
                    item.reference
                )
                existing.technology = (
                    item.technology
                )
                existing.medium = item.medium
                existing.connection_type = (
                    item.connection_type
                )
                existing.capacity = (
                    item.capacity
                )
                existing.geometry = (
                    item.geometry
                )

                updated += 1

            else:

                self.repository.add(
                    item
                )

                inserted += 1

        # --------------------------------------------------
        # Commit
        # --------------------------------------------------

        self.repository.session.commit()

        elapsed = round(
            time.perf_counter()
            - start_time,
            2,
        )

        logger.info(
            "OSM infrastructure import completed. "
            "Inserted: %s, Updated: %s",
            inserted,
            updated,
        )

        return {
            "processed": len(
                infrastructure
            ),
            "inserted": inserted,
            "updated": updated,
            "duplicates_removed": (
                duplicates_removed
            ),
            "failed": 0,
            "country_code": country_code,
            "execution_time": elapsed,
        }