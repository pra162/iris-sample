from app.config.paths import DataPaths
from app.transformers.overpass_transformer import (
    OverpassTransformer,
)


def run(
    paths: DataPaths | None = None,
):

    paths = paths or DataPaths()

    transformer = OverpassTransformer(
        paths=paths,
    )

    return transformer.transform()