from __future__ import annotations

import logging
import time
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models.facility import Facility
from app.database.repositories.facility_repository import (
    FacilityRepository,
)
from app.parsers.facility_parser import FacilityParser


logger = logging.getLogger(__name__)


class FacilityLoader:
    """
    Loads facility data into PostgreSQL.

    The loader is idempotent.

    Existing facilities are identified by:

        source_id

    Existing records are updated.

    New source IDs are inserted.

    Therefore the same source file can safely be
    loaded multiple times.
    """

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

        self.repository = FacilityRepository(
            session
        )

        self.parser = FacilityParser()

    # ======================================================
    # DEDUPLICATION
    # ======================================================

    def _deduplicate(
        self,
        facilities: list[Facility],
    ) -> tuple[list[Facility], int]:

        unique: dict[int, Facility] = {}

        duplicates = 0

        for facility in facilities:

            source_id = facility.source_id

            if source_id in unique:

                duplicates += 1

                logger.warning(
                    "Duplicate source_id skipped: %s",
                    source_id,
                )

                continue

            unique[source_id] = facility

        return (
            list(unique.values()),
            duplicates,
        )

    # ======================================================
    # UPDATE EXISTING FACILITY
    # ======================================================

    def _update_facility(
        self,
        existing: Facility,
        incoming: Facility,
    ) -> None:

        existing.country_code = (
            incoming.country_code
        )

        existing.company = (
            incoming.company
        )

        existing.name = (
            incoming.name
        )

        existing.address = (
            incoming.address
        )

        existing.city = (
            incoming.city
        )

        existing.postal_code = (
            incoming.postal_code
        )

        existing.country = (
            incoming.country
        )

        existing.website = (
            incoming.website
        )

        existing.latitude = (
            incoming.latitude
        )

        existing.longitude = (
            incoming.longitude
        )

        existing.geometry = (
            incoming.geometry
        )

    # ======================================================
    # LOAD
    # ======================================================

    def load(
        self,
        file_path: str | Path,
    ) -> dict:

        start_time = time.perf_counter()

        logger.info(
            "Reading facility file: %s",
            file_path,
        )

        parsed_facilities = (
            self.parser.parse(
                file_path
            )
        )

        logger.info(
            "Parsed %s facilities",
            len(parsed_facilities),
        )

        # --------------------------------------------------
        # Deduplicate incoming source data
        # --------------------------------------------------

        facilities, duplicates = (
            self._deduplicate(
                parsed_facilities
            )
        )

        inserted = 0
        updated = 0

        try:

            # --------------------------------------------------
            # Process every facility
            # --------------------------------------------------

            for incoming in facilities:

                existing = (
                    self.repository.find_by_source_id(
                        incoming.source_id
                    )
                )

                if existing is None:

                    self.session.add(
                        incoming
                    )

                    inserted += 1

                else:

                    self._update_facility(
                        existing,
                        incoming,
                    )

                    updated += 1

            # --------------------------------------------------
            # Commit entire import
            # --------------------------------------------------

            self.session.commit()

        except Exception:

            self.session.rollback()

            logger.exception(
                "Facility import failed."
            )

            raise

        elapsed = round(
            time.perf_counter()
            - start_time,
            2,
        )

        logger.info(
            "Facility import completed."
        )

        return {

            "processed": len(
                parsed_facilities
            ),

            "inserted": inserted,

            "updated": updated,

            "duplicates_removed": duplicates,

            "failed": 0,

            "execution_time": elapsed,
        }