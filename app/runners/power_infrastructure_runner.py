from app.config.paths import DataPaths
from app.commands.load_power_infrastructure_command import (
    LoadPowerInfrastructureCommand,
)
from app.database.session import SessionLocal


def run(
    paths: DataPaths | None = None,
):

    paths = paths or DataPaths()

    session = SessionLocal()

    try:

        command = LoadPowerInfrastructureCommand(
            session,
            paths=paths,
        )

        return command.execute()

    finally:

        session.close()