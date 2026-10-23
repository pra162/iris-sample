from app.config.paths import DataPaths
from app.scrapers.overpass.overpass_parser import (
    OverpassParser,
)


def run(
    paths: DataPaths | None = None,
):
    """
    Run the Overpass parser.

    When called from `all`, the pipeline provides the
    current RunContext-specific DataPaths.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    parser = OverpassParser(
        paths=paths,
    )

    return parser.parse()