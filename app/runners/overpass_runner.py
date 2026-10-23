from app.config.paths import DataPaths
from app.scrapers.overpass.overpass_scraper import (
    OverpassScraper,
)


def run(
    country_code: str = "DE",
    paths: DataPaths | None = None,
):
    """
    Run the Overpass data acquisition.

    When called from `all`, the pipeline provides the
    current RunContext-specific DataPaths.

    When called independently, the default data/
    workspace is used.
    """

    country_code = country_code.upper()

    paths = paths or DataPaths()

    scraper = OverpassScraper(
        country_code=country_code,
        paths=paths,
    )

    return scraper.scrape()