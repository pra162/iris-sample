from __future__ import annotations

import json

import geopandas as gpd
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon

from app.config.paths import DataPaths
from app.database.models.land_value import LandValue


class LandValueParser:
    """
    Parses processed BORIS land-value polygons
    into LandValue SQLAlchemy entities.

    Input:

        <run>/processed/boris/land_values.geojson

    DataPaths controls the input workspace so each
    pipeline execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.file = (
            self.paths.boris_processed
            / "land_values.geojson"
        )

    # ========================================================
    # PARSE
    # ========================================================

    def parse(self) -> list[LandValue]:

        if not self.file.exists():

            raise FileNotFoundError(
                f"Land values file not found:\n"
                f"{self.file}"
            )

        print("--------------------------------")
        print(
            "Loading Land Values..."
        )

        gdf = self._read_geojson()

        print(
            f"Loaded {len(gdf)} "
            f"land value polygons."
        )

        entities: list[LandValue] = []

        skipped = 0

        for _, row in gdf.iterrows():

            geometry = row.geometry

            if geometry is None:

                skipped += 1
                continue

            # ------------------------------------------------
            # Database expects MULTIPOLYGON
            # ------------------------------------------------

            if geometry.geom_type == "Polygon":

                geometry = MultiPolygon(
                    [geometry]
                )

            elif geometry.geom_type != "MultiPolygon":

                skipped += 1
                continue

            entity = LandValue(

                country_code="DE",

                municipality=self._clean_value(
                    row.get("municipality")
                ),

                district=self._clean_value(
                    row.get("district")
                ),

                postal_code=self._clean_value(
                    row.get("postal_code")
                ),

                land_value_eur_m2=self._to_float(
                    row.get(
                        "land_value_eur_m2"
                    )
                ),

                geometry=from_shape(
                    geometry,
                    srid=25832,
                ),
            )

            entities.append(
                entity
            )

        print(
            f"Parsed {len(entities)} "
            f"land values."
        )

        print(
            f"Skipped {skipped} "
            f"invalid geometries."
        )

        return entities

    # ========================================================
    # GEOJSON READER
    # ========================================================

    def _read_geojson(
        self,
    ) -> gpd.GeoDataFrame:

        with self.file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if data.get(
            "type"
        ) != "FeatureCollection":

            raise ValueError(
                "Expected GeoJSON "
                "FeatureCollection."
            )

        features = data.get(
            "features",
            [],
        )

        return gpd.GeoDataFrame.from_features(
            features,
            crs="EPSG:25832",
        )

    # ========================================================
    # VALUE CLEANING
    # ========================================================

    @staticmethod
    def _clean_value(
        value,
    ):

        if value is None:
            return None

        try:

            if value != value:
                return None

        except Exception:
            pass

        return (
            str(value).strip()
            or None
        )

    # ========================================================
    # FLOAT CONVERSION
    # ========================================================

    @staticmethod
    def _to_float(
        value,
    ) -> float | None:

        if value is None:
            return None

        try:

            if value != value:
                return None

        except Exception:
            pass

        try:

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None