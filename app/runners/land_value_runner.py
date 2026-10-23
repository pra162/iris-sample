from app.config.paths import DataPaths
from app.commands.load_land_values_command import (
    LoadLandValuesCommand,
)
from app.database.session import SessionLocal


def run(
    paths: DataPaths | None = None,
):

    paths = paths or DataPaths()

    session = SessionLocal()

    try:

        command = LoadLandValuesCommand(
            session,
            paths=paths,
        )

        return command.execute()

    finally:

        session.close()