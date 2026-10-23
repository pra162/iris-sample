import json

from app.config.data_sources import get_data_source
from app.config.paths import DataPaths
from app.scrapers.base.http_client import HttpClient


class MaStRScraper:
    """
    Scrapes public MaStR data.

    Raw responses are stored in the workspace provided
    by DataPaths.

    Default:

        data/raw/mastr/

    Pipeline run:

        data/runs/<run_id>/raw/mastr/
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.client = HttpClient()

        self.source = get_data_source(
            "mastr"
        )

        # -------------------------------------------------
        # Run-specific output directory
        # -------------------------------------------------

        self.output_dir = (
            self.paths.mastr_raw
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # SCRAPE
    # =====================================================

    def scrape(
        self,
        start_page: int = 1,
        max_pages: int = 5,
        page_size: int = 20,
    ):

        if not self.source.urls:

            raise ValueError(
                "No URL configured for MaStR data source."
            )

        url = self.source.urls[0]

        for page in range(
            start_page,
            start_page + max_pages,
        ):

            print(
                f"Downloading page {page}..."
            )

            response = self.client.get(
                url,
                params={
                    "sort": (
                        "EinheitMeldeDatum-desc"
                    ),
                    "page": page,
                    "pageSize": page_size,
                    "group": "",
                    "filter": "",
                },
            )

            data = response.json()

            output_file = (
                self.output_dir
                / f"page_{page}.json"
            )

            with output_file.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                f"Saved {output_file}"
            )

        print("--------------------------------")
        print(
            "MaStR scraping completed."
        )

        print(
            f"Output Directory : "
            f"{self.output_dir}"
        )