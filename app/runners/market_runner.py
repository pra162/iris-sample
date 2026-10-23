import json

from app.config.paths import DataPaths
from app.scrapers.datacentermap.market_scraper import (
    MarketScraper,
)


def run_markets(
    country_code: str = "DE",
    paths: DataPaths | None = None,
):
    """
    Extract DataCenterMap markets from the country dataset.

    Input:

        <run>/raw/datacentermap/de.json

    Output:

        <run>/processed/datacentermap/de_markets.json

    DataPaths controls the actual storage location.
    """

    country_code = country_code.upper()

    paths = paths or DataPaths()

    scraper = MarketScraper(
        country_code=country_code,
        paths=paths,
    )

    markets = scraper.scrape()

    output_dir = (
        paths.datacentermap_processed
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / f"{country_code.lower()}_markets.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            markets,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("--------------------------------")
    print(
        f"Markets : {len(markets)}"
    )

    print(
        f"Saved   : {output_file}"
    )

    print("--------------------------------")

    return markets