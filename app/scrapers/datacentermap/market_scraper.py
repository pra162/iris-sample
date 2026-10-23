import json
from pathlib import Path

from app.config.paths import DataPaths


class MarketScraper:

    def __init__(
        self,
        country_code: str = "DE",
        paths: DataPaths | None = None,
    ):

        self.country_code = (
            country_code.upper()
        )

        self.paths = paths or DataPaths()

        self.input_file = (
            self.paths.datacentermap_raw
            / f"{self.country_code.lower()}.json"
        )

    def scrape(self):

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"Country data not found: "
                f"{self.input_file}"
            )

        with self.input_file.open(
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        geos = (
            data
            .get("props", {})
            .get("pageProps", {})
            .get("mapdata", {})
            .get("geos", [])
        )

        markets = []

        for geo in geos:

            props = geo.get(
                "properties",
                {}
            )

            coords = (
                geo
                .get("geometry", {})
                .get(
                    "coordinates",
                    [None, None],
                )
            )

            markets.append(
                {
                    "name": props.get("name"),

                    "slug": props.get("link"),

                    "datacenters": props.get(
                        "datacenters"
                    ),

                    "latitude": (
                        coords[1]
                        if len(coords) > 1
                        else None
                    ),

                    "longitude": (
                        coords[0]
                        if len(coords) > 0
                        else None
                    ),

                    "country_code": (
                        self.country_code
                    ),
                }
            )

        return markets