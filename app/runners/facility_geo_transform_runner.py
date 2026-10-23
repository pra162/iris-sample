from app.config.paths import DataPaths
from app.transformers.facility_geo_transformer import (
    FacilityGeoTransformer,
)


def run(
    paths: DataPaths | None = None,
):
    """
    Run the facility geo transformation.

    When called from `all`, the pipeline provides the
    current RunContext-specific DataPaths.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    transformer = FacilityGeoTransformer(
        paths=paths,
    )

    return transformer.transform()