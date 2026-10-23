from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from app.config.data_sources import get_data_source
from app.config.paths import DataPaths


class FacilityTransformer:
    """
    Cleans and normalizes Data Center Map facility data.

    Input:
        <run>/processed/datacentermap/facilities.json

    Output:
        <run>/processed/datacentermap/facilities_clean.json

    Responsibilities:
        - Clean text fields
        - Fix UTF-8 / Windows-1252 mojibake
        - Normalize known city aliases
        - Normalize coordinates
        - Normalize Data Center Map URLs
        - Remove unmapped/placeholder facilities
        - Remove duplicate facility records
        - Preserve source facility IDs
    """

    # =====================================================
    # Data source
    # =====================================================

    DATA_SOURCE_NAME = "datacentermap_facilities"

    # =====================================================
    # Known city aliases
    # =====================================================

    CITY_ALIASES = {
        "Munich": "München",
        "München": "München",

        "Nuremberg": "Nürnberg",
        "Nuernberg": "Nürnberg",
        "Nürnberg": "Nürnberg",

        "Dusseldorf": "Düsseldorf",
        "Düsseldorf": "Düsseldorf",

        "Cologne": "Köln",
        "Köln": "Köln",

        "Wuerzburg": "Würzburg",
        "Wurzburg": "Würzburg",
        "Würzburg": "Würzburg",

        "Lorrach": "Lörrach",
        "Lörrach": "Lörrach",

        "Russelsheim": "Rüsselsheim",
        "Rüsselsheim": "Rüsselsheim",

        "Saarbruecken": "Saarbrücken",
        "Saarbrücken": "Saarbrücken",

        "Fuerth": "Fürth",
        "Fürth": "Fürth",

        "Boblingen": "Böblingen",
        "Böblingen": "Böblingen",

        "Dueren": "Düren",
        "Düren": "Düren",

        "Donauwoerth": "Donauwörth",
        "Donauwörth": "Donauwörth",

        "Goeppingen": "Göppingen",
        "Göppingen": "Göppingen",

        "Guetersloh": "Gütersloh",
        "Gütersloh": "Gütersloh",

        "Moenchengladbach": "Mönchengladbach",
        "Mönchengladbach": "Mönchengladbach",

        "Muenster": "Münster",
        "Münster": "Münster",

        "Neusaess": "Neusäß",
        "Neusäß": "Neusäß",

        "Schoeneck": "Schöneck",
        "Schöneck": "Schöneck",

        "Schwaebisch Gmuend": "Schwäbisch Gmünd",
        "Schwäbisch Gmünd": "Schwäbisch Gmünd",

        "Tuebingen": "Tübingen",
        "Tübingen": "Tübingen",

        "Unterschleissheim": "Unterschleißheim",
        "Unterschleißheim": "Unterschleißheim",

        "Veitshoechheim": "Veitshöchheim",
        "Veitshöchheim": "Veitshöchheim",

        "Halle (Saale)": "Halle (Saale)",
    }

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(
        self,
        paths: DataPaths | None = None,
        input_file: Path | None = None,
        output_file: Path | None = None,
    ):

        self.paths = paths or DataPaths()

        self.input_file = (
            input_file
            or (
                self.paths.datacentermap_processed
                / "facilities.json"
            )
        )

        self.output_file = (
            output_file
            or (
                self.paths.datacentermap_processed
                / "facilities_clean.json"
            )
        )

        self.source = get_data_source(
            self.DATA_SOURCE_NAME
        )

        self.url_template = (
            self.source.urls[0]
        )

        self.url_base = (
            self._build_url_base(
                self.url_template
            )
        )

    # =====================================================
    # Main transformation
    # =====================================================

    def transform(self) -> list[dict]:

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"Facility input file not found: "
                f"{self.input_file}"
            )

        print(
            f"Reading facilities from: "
            f"{self.input_file}"
        )

        with open(
            self.input_file,
            "r",
            encoding="utf-8",
        ) as file:

            facilities = json.load(file)

        if not isinstance(
            facilities,
            list,
        ):

            raise ValueError(
                "Expected facilities.json to contain "
                "a list of facilities."
            )

        print(
            f"Raw facilities loaded: "
            f"{len(facilities)}"
        )

        cleaned: list[dict] = []

        seen_source_ids: set[str] = set()
        seen_fallback_keys: set[tuple] = set()

        skipped_unmapped = 0
        skipped_duplicates = 0
        missing_coordinates = 0

        for facility in facilities:

            if not isinstance(
                facility,
                dict,
            ):
                continue

            # -------------------------------------------------
            # Source ID
            # -------------------------------------------------

            source_id = self._clean_source_id(
                facility.get("id")
            )

            # -------------------------------------------------
            # Name
            # -------------------------------------------------

            name = self._clean_text(
                facility.get("name")
            )

            # -------------------------------------------------
            # Unmapped Data Center records
            # -------------------------------------------------

            if self._is_unmapped_facility(
                source_id=source_id,
                name=name,
            ):

                skipped_unmapped += 1
                continue

            # -------------------------------------------------
            # Text fields
            # -------------------------------------------------

            company = self._clean_text(
                facility.get("company")
            )

            address = self._clean_text(
                facility.get("address")
            )

            city = self._normalize_city(
                facility.get("city")
            )

            country = self._clean_text(
                facility.get("country")
            )

            postal_code = self._clean_text(
                facility.get("postal_code")
            )

            company_slug = self._clean_text(
                facility.get("company_slug")
            )

            listing_type = self._clean_text(
                facility.get("listing_type")
            )

            capacity_type = self._clean_text(
                facility.get("capacity_type")
            )

            slug = self._clean_text(
                facility.get("slug")
            )

            description = self._clean_text(
                facility.get("description")
            )

            # -------------------------------------------------
            # Coordinates
            # -------------------------------------------------

            latitude = self._to_float(
                facility.get("latitude")
            )

            longitude = self._to_float(
                facility.get("longitude")
            )

            if not self._valid_coordinates(
                latitude,
                longitude,
            ):

                missing_coordinates += 1

            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            website = self._normalize_url(
                facility.get("url")
            )

            # -------------------------------------------------
            # Required fields
            # -------------------------------------------------

            if not name:
                name = "Unnamed Facility"

            if not company:
                company = "Unknown"

            # -------------------------------------------------
            # Duplicate detection
            # -------------------------------------------------

            if source_id:

                if source_id in seen_source_ids:

                    skipped_duplicates += 1
                    continue

                seen_source_ids.add(
                    source_id
                )

            else:

                fallback_key = (
                    company,
                    name,
                    city,
                    latitude,
                    longitude,
                )

                if (
                    fallback_key
                    in seen_fallback_keys
                ):

                    skipped_duplicates += 1
                    continue

                seen_fallback_keys.add(
                    fallback_key
                )

            # -------------------------------------------------
            # Clean facility
            # -------------------------------------------------

            cleaned_facility = {
                "id": source_id,
                "company": company,
                "company_slug": company_slug,
                "name": name,
                "listing_type": listing_type,
                "capacity_type": capacity_type,
                "slug": slug,
                "url": website,
                "address": address,
                "postal_code": postal_code,
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
            }

            cleaned.append(
                cleaned_facility
            )

        # -----------------------------------------------------
        # Save output
        # -----------------------------------------------------

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.output_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                cleaned,
                file,
                indent=2,
                ensure_ascii=False,
            )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        print()
        print("=" * 60)
        print(
            "Facility Transformation Summary"
        )
        print("=" * 60)

        print(
            f"Raw facilities:             "
            f"{len(facilities)}"
        )

        print(
            f"Unmapped skipped:           "
            f"{skipped_unmapped}"
        )

        print(
            f"Duplicates skipped:        "
            f"{skipped_duplicates}"
        )

        print(
            f"Missing coordinates:       "
            f"{missing_coordinates}"
        )

        print(
            f"Clean facilities:           "
            f"{len(cleaned)}"
        )

        print(
            f"Output:                     "
            f"{self.output_file}"
        )

        print("=" * 60)

        return cleaned

    # =====================================================
    # Text cleaning
    # =====================================================

    def _clean_text(
        self,
        value,
    ) -> str | None:

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        value = self._fix_mojibake(
            value
        )

        value = self._normalize_whitespace(
            value
        )

        return value

    # =====================================================
    # Mojibake correction
    # =====================================================

    def _fix_mojibake(
        self,
        value: str,
    ) -> str:

        if not value:
            return value

        for _ in range(2):

            if not self._looks_like_mojibake(
                value
            ):
                break

            try:

                fixed = (
                    value
                    .encode("cp1252")
                    .decode("utf-8")
                )

            except (
                UnicodeEncodeError,
                UnicodeDecodeError,
            ):

                break

            if fixed == value:
                break

            value = fixed

        return value

    # =====================================================
    # Mojibake detection
    # =====================================================

    def _looks_like_mojibake(
        self,
        value: str,
    ) -> bool:

        markers = (
            "Ã",
            "Â",
            "â",
            "ð",
        )

        return any(
            marker in value
            for marker in markers
        )

    # =====================================================
    # Whitespace normalization
    # =====================================================

    def _normalize_whitespace(
        self,
        value: str,
    ) -> str:

        return " ".join(
            value.split()
        )

    # =====================================================
    # City normalization
    # =====================================================

    def _normalize_city(
        self,
        value,
    ) -> str | None:

        city = self._clean_text(
            value
        )

        if not city:
            return None

        normalized = (
            self.CITY_ALIASES.get(
                city
            )
        )

        if normalized:
            return normalized

        return city

    # =====================================================
    # Source ID cleaning
    # =====================================================

    def _clean_source_id(
        self,
        value,
    ) -> str | None:

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value

    # =====================================================
    # Unmapped facility detection
    # =====================================================

    def _is_unmapped_facility(
        self,
        source_id: str | None,
        name: str | None,
    ) -> bool:

        if source_id is not None:
            return False

        if not name:
            return True

        normalized_name = (
            name
            .strip()
            .lower()
        )

        return normalized_name in {
            "unmapped data centers",
            "unmapped data center",
        }

    # =====================================================
    # Numeric conversion
    # =====================================================

    def _to_float(
        self,
        value,
    ) -> float | None:

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return None

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            if not value:
                return None

            if value.lower() in {
                "null",
                "none",
                "nan",
            }:

                return None

        try:

            number = float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None

        return number

    # =====================================================
    # Coordinate validation
    # =====================================================

    def _valid_coordinates(
        self,
        latitude: float | None,
        longitude: float | None,
    ) -> bool:

        if latitude is None:
            return False

        if longitude is None:
            return False

        if not -90 <= latitude <= 90:
            return False

        if not -180 <= longitude <= 180:
            return False

        return True

    # =====================================================
    # URL base
    # =====================================================

    def _build_url_base(
        self,
        url_template: str,
    ) -> str:

        parsed = urlsplit(
            url_template
        )

        if (
            not parsed.scheme
            or not parsed.netloc
        ):

            raise ValueError(
                "Data Center Map URL template must "
                "contain a valid absolute URL."
            )

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}/"
        )

    # =====================================================
    # URL normalization
    # =====================================================

    def _normalize_url(
        self,
        url,
    ) -> str | None:

        url = self._clean_text(
            url
        )

        if not url:
            return None

        if url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return url

        return urljoin(
            self.url_base,
            url,
        )