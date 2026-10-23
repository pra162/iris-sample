import json
import random
import time

from app.config.paths import DataPaths
from app.scrapers.datacentermap.facility_scraper import (
    FacilityScraper,
)


class FacilityRunner:
    """
    Runs DataCenterMap facility acquisition.

    Responsibilities:

    - Load market list from the current DataPaths
    - Process markets sequentially
    - Reuse locally cached facility data
    - Rate-limit fresh external requests
    - Show progress
    - Preserve successfully downloaded market files
    - Continue after individual failures
    - Report failed markets at the end

    HTTP retry handling belongs to HttpClient.
    """

    REQUEST_DELAY_MIN = 8
    REQUEST_DELAY_MAX = 15

    def __init__(
        self,
        country_code: str = "DE",
        paths: DataPaths | None = None,
    ):

        self.country_code = country_code.upper()

        self.paths = paths or DataPaths()

        self.markets_file = (
            self.paths.datacentermap_processed
            / f"{self.country_code.lower()}_markets.json"
        )

        self.scraper = FacilityScraper(
            paths=self.paths,
        )

        self.failed_markets: list[str] = []

        self.successful_markets: list[str] = []

        self.skipped_markets: list[str] = []

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        markets = self._load_markets()

        total = len(markets)

        print("--------------------------------")
        print(
            f"Facility Markets : {total}"
        )

        print(
            "Fresh Request Delay : "
            f"{self.REQUEST_DELAY_MIN}-"
            f"{self.REQUEST_DELAY_MAX}s"
        )

        print(
            "Cached Facilities   : No delay"
        )

        print("--------------------------------")

        for index, market in enumerate(
            markets,
            start=1,
        ):

            slug = market.get("slug")

            if not slug:

                self.skipped_markets.append(
                    "<missing-slug>"
                )

                print(
                    f"[{index}/{total}] "
                    "⚠ Skipping market without slug"
                )

                continue

            print(
                f"[{index}/{total}] "
                f"Processing: {slug}"
            )

            try:

                result = self.scraper.scrape_market(
                    slug
                )

                if result is None:

                    self.failed_markets.append(
                        slug
                    )

                    print(
                        f"[{index}/{total}] "
                        f"❌ Failed: {slug}"
                    )

                else:

                    self.successful_markets.append(
                        slug
                    )

                    print(
                        f"[{index}/{total}] "
                        f"✓ Completed: {slug}"
                    )

            except Exception as exc:

                self.failed_markets.append(
                    slug
                )

                print(
                    f"[{index}/{total}] "
                    f"❌ Exception for {slug}: "
                    f"{type(exc).__name__}: {exc}"
                )

            # -------------------------------------------------
            # Delay only when a fresh HTTP request was made.
            #
            # Cached facilities should not cause an artificial
            # delay.
            # -------------------------------------------------

            if (
                index < total
                and self.scraper.last_request_was_external
            ):

                delay = random.uniform(
                    self.REQUEST_DELAY_MIN,
                    self.REQUEST_DELAY_MAX,
                )

                print(
                    f"Waiting {delay:.1f}s "
                    "before next external request..."
                )

                time.sleep(delay)

        self._print_summary()

        return len(
            self.failed_markets
        ) == 0

    # =====================================================
    # LOAD MARKETS
    # =====================================================

    def _load_markets(self):

        if not self.markets_file.exists():

            raise FileNotFoundError(
                f"Markets file not found: "
                f"{self.markets_file}"
            )

        with self.markets_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            markets = json.load(file)

        if not isinstance(
            markets,
            list,
        ):

            raise ValueError(
                f"Expected markets JSON to "
                f"contain a list: "
                f"{self.markets_file}"
            )

        return markets

    # =====================================================
    # SUMMARY
    # =====================================================

    def _print_summary(self):

        print("--------------------------------")
        print(
            "Facility scraping completed."
        )
        print("--------------------------------")

        print(
            f"Successful : "
            f"{len(self.successful_markets)}"
        )

        print(
            f"Failed     : "
            f"{len(self.failed_markets)}"
        )

        print(
            f"Skipped    : "
            f"{len(self.skipped_markets)}"
        )

        if self.failed_markets:

            print("--------------------------------")
            print(
                "Failed markets:"
            )

            for slug in self.failed_markets:

                print(
                    f"  - {slug}"
                )

        print("--------------------------------")


# =========================================================
# PUBLIC RUNNER FUNCTION
# =========================================================

def run_facilities(
    country_code: str = "DE",
    paths: DataPaths | None = None,
):
    """
    Public facility runner used by PipelineRunner.
    """

    runner = FacilityRunner(
        country_code=country_code,
        paths=paths,
    )

    success = runner.run()

    if not success:

        raise RuntimeError(
            "Facility scraping completed with "
            f"{len(runner.failed_markets)} "
            "failed market(s)."
        )

    return runner