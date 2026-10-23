from app.config.paths import DataPaths
from app.database.session import SessionLocal
from app.intelligence.news_intelligence import NewsIntelligence


def run(
    paths: DataPaths | None = None,
):
    """
    Build news intelligence from the database.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    session = SessionLocal()

    try:

        intelligence = NewsIntelligence(
            session,
            paths=paths,
        )

        return intelligence.build()

    finally:

        session.close()