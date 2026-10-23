from app.config.data_sources import get_data_source
from app.config.paths import DataPaths
from app.scrapers.base.http_client import HttpClient
from app.scrapers.base.parser import NextDataParser


class CountryScraper:
    """
    Scrapes country-level DataCenterMap data.

    DataPaths is accepted so the scraper can participate
    in an isolated pipeline run.

    HTTP retry and rate-limit behavior is controlled by
    HttpClient.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.client = HttpClient()

        self.parser = NextDataParser()

        self.source = get_data_source(
            "datacentermap"
        )

    # =====================================================
    # SCRAPE
    # =====================================================

    def scrape(self):

        url = self.source.urls[0]

        response = self.client.get(
            url,
            max_retries=3,
            retry_on_rate_limit=True,
        )

        data = self.parser.parse(
            response.text
        )

        return data