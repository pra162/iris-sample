from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.loaders.osm_infrastructure_loader import (
    OsmInfrastructureLoader,
)


class LoadOsmInfrastructureCommand:

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
        country_code: str = "DE",
    ):

        self.loader = OsmInfrastructureLoader(
            session,
        )

        self.paths = paths
        self.country_code = country_code.upper()

    def execute(self):

        paths = (
            self.paths
            or DataPaths()
        )

        file_path = (
            paths.overpass_processed
            / "telecom_network.geojson"
        )

        return self.loader.load(
            file_path,
            country_code=self.country_code,
        )