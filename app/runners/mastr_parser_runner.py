from app.config.paths import DataPaths
from app.scrapers.mastr.mastr_parser import MaStRParser


def run(
    paths: DataPaths | None = None,
):
    """
    Run the MaStR parser.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    parser = MaStRParser(
        paths=paths,
    )

    return parser.parse()