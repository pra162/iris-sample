import json

from app.config.paths import DataPaths


class FacilityParser:
    """
    Parses raw DataCenterMap facility responses.

    The parser uses DataPaths so it can operate on either:

        data/raw/...

    or an isolated pipeline run:

        data/runs/<run_id>/raw/...
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

    # =====================================================
    # PARSE
    # =====================================================

    def parse(
        self,
        slug: str,
    ):

        file = (
            self.paths.datacentermap_facilities_raw
            / f"{slug}.json"
        )

        if not file.exists():

            raise FileNotFoundError(
                f"Facility file not found: "
                f"{file}"
            )

        with file.open(
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        page_props = (
            data
            .get("props", {})
            .get("pageProps")
        )

        if not page_props:

            print(
                f"⚠ {slug}: missing pageProps"
            )

            return []

        mapdata = page_props.get(
            "mapdata"
        )

        if not mapdata:

            print(
                f"⚠ {slug}: no mapdata"
            )

            return []

        dcs = mapdata.get(
            "dcs",
            []
        )

        if not dcs:

            print(
                f"⚠ {slug}: "
                "no data centers found"
            )

            return []

        facilities = []

        for dc in dcs:

            props = dc.get(
                "properties",
                {}
            )

            geometry = dc.get(
                "geometry",
                {}
            )

            coords = geometry.get(
                "coordinates",
                [None, None],
            )

            latitude = (
                coords[1]
                if len(coords) > 1
                else None
            )

            longitude = (
                coords[0]
                if len(coords) > 0
                else None
            )

            facilities.append(
                {
                    "id": props.get("id"),

                    "name": props.get(
                        "name"
                    ),

                    "company": props.get(
                        "companyname"
                    ),

                    "company_slug": props.get(
                        "companylink"
                    ),

                    "listing_type": props.get(
                        "listingtype"
                    ),

                    "capacity_type": props.get(
                        "capacitytype"
                    ),

                    "slug": props.get(
                        "link"
                    ),

                    "url": props.get(
                        "url"
                    ),

                    "address": props.get(
                        "address"
                    ),

                    "postal_code": props.get(
                        "postal"
                    ),

                    "city": props.get(
                        "city"
                    ),

                    "country": props.get(
                        "country"
                    ),

                    "latitude": latitude,

                    "longitude": longitude,

                    "description": props.get(
                        "oneliner"
                    ),
                }
            )

        return facilities