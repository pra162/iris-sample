from __future__ import annotations

import json

import geopandas as gpd
from shapely.geometry import Point

from app.config.paths import DataPaths


class FacilityGeoTransformer:
    """
    Converts cleaned facility records into a GeoJSON dataset.

    Input:
        <run>/processed/datacentermap/facilities_clean.json

    Output:
        <run>/processed/datacentermap/facilities.geojson

    Responsibilities:
        - Read cleaned facility records
        - Validate coordinates
        - Convert latitude/longitude to Point geometry
        - Preserve all facility attributes
        - Create a WGS84 GeoDataFrame
        - Export facilities with valid coordinates to GeoJSON

    Facilities without valid coordinates are preserved in the
    cleaned JSON and database, but cannot be represented as
    geographic Point features.
    """

    CRS = "EPSG:4326"

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # =================================================
        # Run-specific input/output paths
        # =================================================

        self.input_file = (
            self.paths.datacentermap_processed
            / "facilities_clean.json"
        )

        self.output_dir = (
            self.paths.datacentermap_processed
        )

        self.output_file = (
            self.output_dir
            / "facilities.geojson"
        )

        self.facilities: list[dict] = []

        self.features: list[dict] = []

        self.gdf: gpd.GeoDataFrame | None = None

    # ======================================================
    # TRANSFORM
    # ======================================================

    def transform(self):

        self.load_facilities()

        self.create_features()

        self.create_geodataframe()

        self.save_geojson()

        print("--------------------------------")
        print(
            "Facility Geo Transformation completed."
        )

        return self.gdf

    # ======================================================
    # LOAD
    # ======================================================

    def load_facilities(self):

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"Facility input file not found: "
                f"{self.input_file}"
            )

        with self.input_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            list,
        ):

            raise ValueError(
                "Expected facility JSON to contain a list."
            )

        self.facilities = data

        print("--------------------------------")
        print(
            f"Facilities Loaded : "
            f"{len(self.facilities)}"
        )

    # ======================================================
    # CREATE FEATURES
    # ======================================================

    def create_features(self):

        self.features = []

        skipped = 0

        for facility in self.facilities:

            if not isinstance(
                facility,
                dict,
            ):

                skipped += 1

                continue

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

                skipped += 1

                continue

            feature = facility.copy()

            feature["latitude"] = latitude

            feature["longitude"] = longitude

            feature["geometry"] = Point(
                longitude,
                latitude,
            )

            self.features.append(
                feature
            )

        print("--------------------------------")
        print(
            f"Features Created : "
            f"{len(self.features)}"
        )

        print(
            f"Skipped          : "
            f"{skipped}"
        )

    # ======================================================
    # GEODATAFRAME
    # ======================================================

    def create_geodataframe(self):

        self.gdf = gpd.GeoDataFrame(
            self.features,
            geometry="geometry",
            crs=self.CRS,
        )

        print("--------------------------------")
        print(
            f"GeoDataFrame Rows : "
            f"{len(self.gdf)}"
        )

        print(
            f"CRS               : "
            f"{self.gdf.crs}"
        )

    # ======================================================
    # SAVE
    # ======================================================

    def save_geojson(self):

        if self.gdf is None:

            raise RuntimeError(
                "GeoDataFrame has not been created."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Write GeoJSON directly.
        #
        # This avoids GeoPandas.to_file(), which requires
        # Fiona/Pyogrio and therefore GDAL on this system.
        # --------------------------------------------------

        geojson = self.gdf.to_json(
            ensure_ascii=False,
        )

        self.output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")
        print(
            f"Saved             : "
            f"{self.output_file}"
        )

    # ======================================================
    # FLOAT CONVERSION
    # ======================================================

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

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None

    # ======================================================
    # COORDINATE VALIDATION
    # ======================================================

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