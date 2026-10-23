import json
import shutil
from pathlib import Path

from app.config.paths import DataPaths
from app.scrapers.datacentermap.country_scraper import (
    CountryScraper,
)


def run_country(
    country_code: str = "DE",
    paths: DataPaths | None = None,
):
    """
    Acquire country-level DataCenterMap data.

    Behavior:

    1. If the run-specific country file already exists,
       reuse it.

    2. Otherwise, if legacy/local country data exists at
       data/raw/datacentermap/<country>.json, reuse it.

    3. Otherwise, download fresh data from DataCenterMap.

    This allows the pipeline to continue using previously
    acquired data without repeatedly requesting the external
    source.

    DataPaths controls the run-specific storage location.
    """

    country_code = country_code.upper()

    paths = paths or DataPaths()

    output_dir = paths.datacentermap_raw

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / f"{country_code.lower()}.json"
    )

    # =====================================================
    # EXISTING RUN DATA
    # =====================================================

    if output_file.exists():

        print("--------------------------------")
        print(
            "Country data already exists "
            "in current run."
        )

        print(
            f"Using: {output_file}"
        )

        with output_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # =====================================================
    # LEGACY / LOCAL CACHE
    # =====================================================

    legacy_file = (
        Path("data/raw/datacentermap")
        / f"{country_code.lower()}.json"
    )

    if legacy_file.exists():

        print("--------------------------------")
        print(
            "Using existing local "
            "DataCenterMap country data."
        )

        print(
            f"Source : {legacy_file}"
        )

        print(
            f"Target : {output_file}"
        )

        shutil.copy2(
            legacy_file,
            output_file,
        )

        print("--------------------------------")
        print(
            "Country data reused successfully."
        )
        print("--------------------------------")

        with output_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # =====================================================
    # FRESH ACQUISITION
    # =====================================================

    print(
        f"Country DataCenterMap acquisition: "
        f"{country_code}"
    )

    scraper = CountryScraper(
        paths=paths,
    )

    try:

        data = scraper.scrape()

    except Exception as exc:

        print("--------------------------------")
        print(
            "Country acquisition failed."
        )

        print(
            f"Country : {country_code}"
        )

        print(
            f"Error   : "
            f"{type(exc).__name__}: {exc}"
        )

        print("--------------------------------")

        raise

    # =====================================================
    # SAVE FRESH DATA
    # =====================================================

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

    print("--------------------------------")
    print(
        f"Saved: {output_file}"
    )
    print("--------------------------------")

    return data