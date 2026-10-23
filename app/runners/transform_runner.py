from app.config.paths import DataPaths
from app.transformers.facility_transformer import (
    FacilityTransformer,
)


def run_transform(
    paths: DataPaths | None = None,
):
    """
    Transform merged facility data.

    When called from `all`, the runner receives the
    RunContext-specific DataPaths.

    When called independently, it uses the default
    data/ paths for backward compatibility.
    """

    paths = paths or DataPaths()

    transformer = FacilityTransformer(
        paths=paths,
    )

    return transformer.transform()