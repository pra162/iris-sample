from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.loaders.load_land_values import LoadLandValues


class LoadLandValuesCommand:

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        self.loader = LoadLandValues(
            session,
            paths=paths,
        )

    def execute(self) -> None:

        return self.loader.execute()