from app.config.paths import DataPaths
from app.commands.load_osm_infrastructure_command import (
    LoadOsmInfrastructureCommand,
)
from app.database.session import SessionLocal


def run(
    paths: DataPaths | None = None,
    country_code: str = "DE",
):

    paths = paths or DataPaths()

    session = SessionLocal()

    try:

        command = LoadOsmInfrastructureCommand(
            session,
            paths=paths,
            country_code=country_code,
        )

        return command.execute()

    finally:

        session.close()