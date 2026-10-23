from __future__ import annotations

import json
from pathlib import Path

from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.database.models.facility import Facility


class FacilityParser:
    """
    Parses cleaned facility JSON into Facility SQLAlchemy entities.

    Input:
        data/processed/datacentermap/facilities_clean.json

    Output:
        list[Facility]

    Responsibilities:
        - Read cleaned facility JSON
        - Preserve Data Center Map source ID
        - Map JSON fields to Facility model
        - Set country code
        - Map Data Center Map URL to website
        - Convert coordinates to PostGIS geometry
        - Preserve facilities without coordinates
        - Leave internal UUID generation to SQLAlchemy
    """

    COUNTRY_CODE = "DE"

    def parse(
        self,
        file_path: str | Path,
    ) -> list[Facility]:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Facility file not found: {file_path}"
            )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "Expected facility JSON to contain a list."
            )

        facilities: list[Facility] = []

        for item in data:

            if not isinstance(item, dict):
                continue

            # -------------------------------------------------
            # SOURCE ID
            # -------------------------------------------------

            source_id = self._to_int(
                item.get("id")
            )

            if source_id is None:
                continue

            # -------------------------------------------------
            # REQUIRED FIELDS
            # -------------------------------------------------

            company = (
                item.get("company")
                or "Unknown"
            )

            name = (
                item.get("name")
                or "Unnamed Facility"
            )

            # -------------------------------------------------
            # BASIC FIELDS
            # -------------------------------------------------

            address = item.get(
                "address"
            )

            city = item.get(
                "city"
            )

            postal_code = item.get(
                "postal_code"
            )

            country = item.get(
                "country"
            )

            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            website = item.get(
                "url"
            )

            # -------------------------------------------------
            # COORDINATES
            # -------------------------------------------------

            latitude = self._to_float(
                item.get("latitude")
            )

            longitude = self._to_float(
                item.get("longitude")
            )

            # -------------------------------------------------
            # POSTGIS GEOMETRY
            # -------------------------------------------------

            geometry = None

            if self._valid_coordinates(
                latitude,
                longitude,
            ):

                geometry = from_shape(
                    Point(
                        longitude,
                        latitude,
                    ),
                    srid=4326,
                )

            # -------------------------------------------------
            # SQLALCHEMY ENTITY
            # -------------------------------------------------

            facility = Facility(

                source_id=source_id,

                country_code=self.COUNTRY_CODE,

                company=company,

                name=name,

                address=address,

                city=city,

                postal_code=postal_code,

                country=country,

                website=website,

                latitude=latitude,

                longitude=longitude,

                geometry=geometry,
            )

            facilities.append(
                facility
            )

        return facilities

    # =========================================================
    # INTEGER CONVERSION
    # =========================================================

    def _to_int(
        self,
        value,
    ) -> int | None:

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, str):

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
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # =========================================================
    # FLOAT CONVERSION
    # =========================================================

    def _to_float(
        self,
        value,
    ) -> float | None:

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, str):

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
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # =========================================================
    # COORDINATE VALIDATION
    # =========================================================

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