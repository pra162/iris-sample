from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.parsers.power_infrastructure_parser import (
    PowerInfrastructureParser,
)
from app.database.repositories.power_infrastructure_repository import (
    PowerInfrastructureRepository,
)


class LoadPowerInfrastructure:
    """
    Loads processed OpenStreetMap power infrastructure
    into PostgreSQL.
    """

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        paths = paths or DataPaths()

        self.parser = PowerInfrastructureParser(
            paths=paths,
        )

        self.repository = PowerInfrastructureRepository(
            session
        )

    def execute(self):

        print("--------------------------------")
        print(
            "Loading Power Infrastructure"
        )

        entities = self.parser.parse()

        print(
            "Deleting existing power infrastructure..."
        )

        self.repository.delete_all()

        print(
            f"Inserting {len(entities)} "
            "power infrastructure..."
        )

        self.repository.create_many(
            entities
        )

        print("--------------------------------")
        print(
            "Power Infrastructure "
            "Loaded Successfully"
        )