import json
import shutil
from pathlib import Path

from app.config.data_sources import get_data_source
from app.config.paths import DataPaths
from app.scrapers.base.http_client import HttpClient
from app.scrapers.base.parser import NextDataParser


class FacilityScraper:
    """
    Scrapes DataCenterMap facility data for individual markets.

    Behavior:

    1. Reuse data already present in the current pipeline run.
    2. Reuse previously acquired local facility data.
    3. Download from DataCenterMap only when no local data exists.

    This prevents unnecessary external requests and allows
    isolated pipeline runs to reuse previously acquired data.
    """

    LEGACY_FACILITIES_DIR = Path(
        "data/raw/datacentermap/facilities"
    )

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.client = HttpClient()

        self.parser = NextDataParser()

        self.source = get_data_source(
            "datacentermap_facilities"
        )

        # Used by FacilityRunner to determine whether
        # a real external request was made.
        self.last_request_was_external = False

    # =====================================================
    # SCRAPE MARKET
    # =====================================================

    def scrape_market(
        self,
        slug: str,
    ):

        # Reset request state for every market.
        self.last_request_was_external = False

        output_dir = (
            self.paths.datacentermap_facilities_raw
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_dir
            / f"{slug}.json"
        )

        # =================================================
        # CURRENT RUN CACHE
        # =================================================

        if output_file.exists():

            print(
                f"✓ Using existing run data: "
                f"{output_file}"
            )

            with output_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        # =================================================
        # LEGACY LOCAL CACHE
        # =================================================

        legacy_file = (
            self.LEGACY_FACILITIES_DIR
            / f"{slug}.json"
        )

        if legacy_file.exists():

            print(
                f"✓ Reusing local facility data: "
                f"{legacy_file}"
            )

            shutil.copy2(
                legacy_file,
                output_file,
            )

            print(
                f"✓ Copied to: {output_file}"
            )

            with output_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        # =================================================
        # FRESH DOWNLOAD
        # =================================================

        url_template = self.source.urls[0]

        url = url_template.format(
            slug=slug
        )

        print(
            f"Downloading: {url}"
        )

        # This is an actual external request.
        self.last_request_was_external = True

        try:

            response = self.client.get(
                url,
                max_retries=3,
                retry_on_rate_limit=True,
            )

            data = self.parser.parse(
                response.text
            )

            page_props = (
                data
                .get(
                    "props",
                    {}
                )
                .get(
                    "pageProps",
                    {}
                )
            )

            # ------------------------------------------------
            # Skip invalid pages
            # ------------------------------------------------

            if "mapdata" not in page_props:

                print(
                    f"⚠ Skipping {slug}: "
                    "no facility data found."
                )

                return None

            # ------------------------------------------------
            # Save raw response
            # ------------------------------------------------

            with output_file.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(
                f"✅ Saved: {output_file}"
            )

            return data

        except Exception as exc:

            print(
                f"❌ Failed downloading "
                f"{slug}: {exc}"
            )

            return None