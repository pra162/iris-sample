from app.config.paths import DataPaths

from app.scrapers.mastr.mastr_scraper import (
    MaStRScraper,
)

from app.scrapers.mastr.mastr_parser import (
    MaStRParser,
)


def run(
    paths: DataPaths | None = None,
):
    """
    Run the MaStR acquisition and parsing pipeline.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    # =====================================================
    # SCRAPER
    # =====================================================

    scraper = MaStRScraper(
        paths=paths,
    )

    scraper.scrape()

    # =====================================================
    # PARSER
    # =====================================================

    parser = MaStRParser(
        paths=paths,
    )

    return parser.parse()