from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.loaders.news_loader import NewsLoader


class LoadNewsCommand:
    """
    Loads processed news intelligence into PostgreSQL.
    """

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        self.loader = NewsLoader(
            session,
            paths=paths,
        )

    def execute(self):

        return self.loader.execute()