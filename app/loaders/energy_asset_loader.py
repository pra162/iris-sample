from pathlib import Path
import logging
import time

from sqlalchemy.orm import Session

from app.database.repositories.energy_asset_repository import (
    EnergyAssetRepository,
)
from app.parsers.mastr_parser import MaStRParser


logger = logging.getLogger(__name__)


class EnergyAssetLoader:
    """
    Loads MaStR energy assets into PostgreSQL.
    """

    def __init__(self, session: Session):
        self.repository = EnergyAssetRepository(session)
        self.parser = MaStRParser()

    def load(self, file_path: str | Path) -> dict:

        start_time = time.perf_counter()

        logger.info("Reading MaStR file...")

        assets = self.parser.parse(file_path)

        logger.info(
            "Parsed %s energy assets.",
            len(assets),
        )

        # --------------------------------------------------
        # Remove duplicates inside the import file
        # --------------------------------------------------

        unique_assets = []
        seen = set()

        for asset in assets:

            if asset.mastr_number in seen:
                continue

            seen.add(asset.mastr_number)
            unique_assets.append(asset)

        duplicates_removed = (
                len(assets) - len(unique_assets)
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

        for asset in unique_assets:

            existing = (
                self.repository.find_by_mastr_number(
                    asset.mastr_number
                )
            )

            if existing:

                self.repository.update_from_entity(
                    existing,
                    asset,
                )

                updated += 1

            else:

                self.repository.add(asset)

                inserted += 1

        # --------------------------------------------------
        # Commit
        # --------------------------------------------------

        self.repository.session.commit()

        elapsed = round(
            time.perf_counter() - start_time,
            2,
        )

        logger.info(
            "Energy asset import completed. "
            "Inserted: %s, Updated: %s",
            inserted,
            updated,
        )

        return {
            "processed": len(assets),
            "inserted": inserted,
            "updated": updated,
            "duplicates_removed": duplicates_removed,
            "failed": 0,
            "execution_time": elapsed,
        }