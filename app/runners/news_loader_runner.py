from app.config.paths import DataPaths
from app.commands.load_news_command import LoadNewsCommand
from app.database.session import SessionLocal


def run(
    paths: DataPaths | None = None,
):
    """
    Load matched news into PostgreSQL.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    session = SessionLocal()

    try:

        command = LoadNewsCommand(
            session,
            paths=paths,
        )

        return command.execute()

    finally:

        session.close()