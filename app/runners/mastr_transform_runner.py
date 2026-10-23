from app.config.paths import DataPaths
from app.transformers.mastr_transformer import (
    MaStRTransformer,
)


def run(
    country_code: str = "DE",
    paths: DataPaths | None = None,
):
    """
    Run the MaStR transformer.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    country_code = country_code.upper()

    paths = paths or DataPaths()

    transformer = MaStRTransformer(
        country_code=country_code,
        paths=paths,
    )

    return transformer.transform()