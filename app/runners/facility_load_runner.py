from app.commands.load_facilities_command import (
    LoadFacilitiesCommand,
)
from app.database.session import SessionLocal


def run():

    session = SessionLocal()

    try:

        command = LoadFacilitiesCommand(
            session
        )

        return command.execute()

    finally:

        session.close()