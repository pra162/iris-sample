from app.config.paths import DataPaths
from app.transformers.overpass_transformer import (
    OverpassTransformer,
)


def run(
    paths: DataPaths | None = None,
):
    """
    Run the Overpass transformer.

    When called from `all`, the pipeline provides the
    current RunContext-specific DataPaths.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    transformer = OverpassTransformer(
        paths=paths,
    )

    return transformer.transform()