from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.loaders.load_power_infrastructure import (
    LoadPowerInfrastructure,
)


class LoadPowerInfrastructureCommand:

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        self.loader = LoadPowerInfrastructure(
            session,
            paths=paths,
        )

    def execute(self):

        return self.loader.execute()