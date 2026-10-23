from __future__ import annotations

import json

import geopandas as gpd

from app.config.paths import DataPaths
from app.database.models.power_infrastructure import (
    PowerInfrastructure,
)


class PowerInfrastructureParser:
    """
    Parses the processed Overpass power infrastructure GeoJSON
    into PowerInfrastructure entities.

    Source CRS:
        EPSG:4326

    Database CRS:
        EPSG:4326

    DataPaths controls the input workspace so each pipeline
    execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.file = (
            self.paths.overpass_processed
            / "power_grid.geojson"
        )

    # ---------------------------------------------------------
    # PARSE
    # ---------------------------------------------------------

    def parse(
        self,
    ) -> list[PowerInfrastructure]:

        print("--------------------------------")
        print(
            "Loading Power Infrastructure..."
        )

        gdf = self._read_geojson()

        print(
            f"Loaded {len(gdf)} "
            "power infrastructure records."
        )

        infrastructure: list[
            PowerInfrastructure
        ] = []

        skipped = 0

        for _, row in gdf.iterrows():

            if row.geometry is None:

                skipped += 1
                continue

            infrastructure.append(
                self._build_entity(row)
            )

        print(
            f"Parsed {len(infrastructure)} "
            "power infrastructure records."
        )

        print(
            f"Skipped {skipped} "
            "records without geometry."
        )

        return infrastructure

    # ---------------------------------------------------------
    # GEOJSON READER
    # ---------------------------------------------------------

    def _read_geojson(
        self,
    ) -> gpd.GeoDataFrame:

        if not self.file.exists():

            raise FileNotFoundError(
                "Power infrastructure file "
                "not found:\n"
                f"{self.file}"
            )

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
            crs="EPSG:4326",
        )

    # ---------------------------------------------------------
    # ENTITY
    # ---------------------------------------------------------

    def _build_entity(
        self,
        row,
    ) -> PowerInfrastructure:

        geometry = (
            self._geometry_to_ewkt(
                row.geometry
            )
        )

        return PowerInfrastructure(

            country_code="DE",

            osm_id=self._int(
                row.get("osm_id")
            ),

            element_type=self._string(
                row.get("element_type")
            ),

            power_type=self._string(
                row.get("power_type")
            ),

            name=self._string(
                row.get("name")
            ),

            operator=self._string(
                row.get("operator")
            ),

            voltage=self._string(
                row.get("voltage")
            ),

            frequency=self._string(
                row.get("frequency")
            ),

            reference=self._string(
                row.get("reference")
            ),

            geometry=geometry,
        )

    # ---------------------------------------------------------
    # GEOMETRY
    # ---------------------------------------------------------

    @staticmethod
    def _geometry_to_ewkt(
        geometry,
    ) -> str | None:

        if geometry is None:

            return None

        return (
            "SRID=4326;"
            f"{geometry.wkt}"
        )

    # ---------------------------------------------------------
    # STRING
    # ---------------------------------------------------------

    @staticmethod
    def _string(
        value,
    ):

        if value is None:

            return None

        try:

            if value != value:

                return None

        except Exception:

            pass

        value = str(
            value
        ).strip()

        return (
            value
            if value
            else None
        )

    # ---------------------------------------------------------
    # INTEGER
    # ---------------------------------------------------------

    @staticmethod
    def _int(
        value,
    ):

        if value is None:

            return None

        try:

            if value != value:

                return None

            return int(value)

        except (
            TypeError,
            ValueError,
        ):

            return None