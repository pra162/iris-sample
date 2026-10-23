from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.parsers.land_value_parser import LandValueParser
from app.database.repositories.land_value_repository import (
    LandValueRepository,
)


class LoadLandValues:
    """
    Loads processed BORIS land values into PostgreSQL.
    """

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        paths = paths or DataPaths()

        self.parser = LandValueParser(
            paths=paths,
        )

        self.repository = LandValueRepository(
            session
        )

    def execute(self) -> None:

        print("--------------------------------")
        print("Loading Land Values")

        entities = self.parser.parse()

        print(
            "Deleting existing land values..."
        )

        self.repository.delete_all()

        print(
            f"Inserting {len(entities)} "
            "land values..."
        )

        self.repository.create_many(
            entities
        )

        print("--------------------------------")
        print(
            "Land Values Loaded Successfully"
        )