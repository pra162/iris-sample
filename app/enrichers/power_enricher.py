from __future__ import annotations

import json

import geopandas as gpd

from app.config.paths import DataPaths
from app.enrichers.power_score import PowerScore
from app.spatial.nearest import NearestSpatial


class PowerEnricher:
    """
    Enriches data center facilities with nearby power
    infrastructure.

    Inputs:

        <run>/processed/datacentermap/facilities.geojson
        <run>/processed/overpass/power_grid.geojson

    Output:

        <run>/processed/enriched/facilities_power.geojson

    Power enrichment includes:

        - nearest substation
        - nearest power line
        - nearest transformer
        - distance to each asset
        - power readiness score
        - power rating
        - power rank

    GeoJSON is loaded directly through Python JSON instead
    of GeoPandas read_file(), avoiding Fiona/Pyogrio/GDAL
    runtime dependencies on Windows.

    DataPaths controls the workspace so each pipeline run
    remains isolated.
    """

    TARGET_CRS = "EPSG:25832"

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # -------------------------------------------------
        # Input files
        # -------------------------------------------------

        self.facilities_file = (
            self.paths.datacentermap_processed
            / "facilities.geojson"
        )

        self.power_file = (
            self.paths.overpass_processed
            / "power_grid.geojson"
        )

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        self.output_dir = (
            self.paths.enriched
        )

        self.output_file = (
            self.output_dir
            / "facilities_power.geojson"
        )

        # -------------------------------------------------
        # GeoDataFrames
        # -------------------------------------------------

        self.facilities: (
            gpd.GeoDataFrame | None
        ) = None

        self.power: (
            gpd.GeoDataFrame | None
        ) = None

        self.substations: (
            gpd.GeoDataFrame | None
        ) = None

        self.power_lines: (
            gpd.GeoDataFrame | None
        ) = None

        self.transformers: (
            gpd.GeoDataFrame | None
        ) = None

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def enrich(self):

        self.load_facilities()

        self.load_power_grid()

        self.reproject()

        self.filter_power_assets()

        self.enrich_nearest_substation()

        self.enrich_nearest_power_line()

        self.enrich_nearest_transformer()

        self.calculate_power_score()

        self.save()

        print("--------------------------------")
        print(
            "Power enrichment completed."
        )

        return self.facilities

    # =====================================================
    # LOAD FACILITIES
    # =====================================================

    def load_facilities(self):

        self.facilities = (
            self._read_geojson(
                self.facilities_file
            )
        )

        print("--------------------------------")
        print(
            f"Facilities Loaded : "
            f"{len(self.facilities)}"
        )

    # =====================================================
    # LOAD POWER GRID
    # =====================================================

    def load_power_grid(self):

        self.power = (
            self._read_geojson(
                self.power_file
            )
        )

        print("--------------------------------")
        print(
            f"Power Assets Loaded : "
            f"{len(self.power)}"
        )

    # =====================================================
    # GEOJSON READER
    # =====================================================

    def _read_geojson(
        self,
        file_path,
    ) -> gpd.GeoDataFrame:

        if not file_path.exists():

            raise FileNotFoundError(
                f"GeoJSON file not found: "
                f"{file_path}"
            )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if data.get(
            "type"
        ) != "FeatureCollection":

            raise ValueError(
                "Expected GeoJSON "
                "FeatureCollection: "
                f"{file_path}"
            )

        features = data.get(
            "features",
            [],
        )

        # -------------------------------------------------
        # Generated GeoJSON datasets use WGS84.
        #
        # Do not pass the GeoJSON CRS object directly to
        # GeoPandas because some GeoPandas/pyproj versions
        # cannot parse CRS84 metadata correctly.
        # -------------------------------------------------

        gdf = (
            gpd.GeoDataFrame.from_features(
                features
            )
        )

        if gdf.crs is None:

            gdf = gdf.set_crs(
                "EPSG:4326"
            )

        return gdf

    # =====================================================
    # REPROJECT
    # =====================================================

    def reproject(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities have not "
                "been loaded."
            )

        if self.power is None:

            raise RuntimeError(
                "Power infrastructure "
                "has not been loaded."
            )

        self.facilities = (
            self.facilities.to_crs(
                self.TARGET_CRS
            )
        )

        self.power = (
            self.power.to_crs(
                self.TARGET_CRS
            )
        )

        print("--------------------------------")
        print(
            "Reprojection Complete"
        )

        print(
            f"Facilities CRS : "
            f"{self.facilities.crs}"
        )

        print(
            f"Power CRS      : "
            f"{self.power.crs}"
        )

    # =====================================================
    # FILTER POWER ASSETS
    # =====================================================

    def filter_power_assets(self):

        if self.power is None:

            raise RuntimeError(
                "Power infrastructure "
                "has not been loaded."
            )

        if "power_type" not in (
            self.power.columns
        ):

            raise ValueError(
                "Power GeoJSON does not contain "
                "'power_type'."
            )

        self.substations = (
            self.power[
                self.power["power_type"]
                == "substation"
            ].copy()
        )

        self.power_lines = (
            self.power[
                self.power["power_type"]
                == "line"
            ].copy()
        )

        self.transformers = (
            self.power[
                self.power["power_type"]
                == "transformer"
            ].copy()
        )

        print("--------------------------------")

        print(
            f"Substations : "
            f"{len(self.substations)}"
        )

        print(
            f"Power Lines : "
            f"{len(self.power_lines)}"
        )

        print(
            f"Transformers: "
            f"{len(self.transformers)}"
        )

    # =====================================================
    # NEAREST SUBSTATION
    # =====================================================

    def enrich_nearest_substation(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities are not loaded."
            )

        if self.substations is None:

            raise RuntimeError(
                "Substations are not prepared."
            )

        self.facilities = (
            NearestSpatial.find_nearest(
                source_gdf=self.facilities,
                target_gdf=self.substations,
                target_type="substation",
                name_column="name",
            )
        )

    # =====================================================
    # NEAREST POWER LINE
    # =====================================================

    def enrich_nearest_power_line(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities are not loaded."
            )

        if self.power_lines is None:

            raise RuntimeError(
                "Power lines are not prepared."
            )

        self.facilities = (
            NearestSpatial.find_nearest(
                source_gdf=self.facilities,
                target_gdf=self.power_lines,
                target_type="power_line",
                name_column="reference",
            )
        )

    # =====================================================
    # NEAREST TRANSFORMER
    # =====================================================

    def enrich_nearest_transformer(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities are not loaded."
            )

        if self.transformers is None:

            raise RuntimeError(
                "Transformers are not prepared."
            )

        self.facilities = (
            NearestSpatial.find_nearest(
                source_gdf=self.facilities,
                target_gdf=self.transformers,
                target_type="transformer",
                name_column="name",
            )
        )

    # =====================================================
    # POWER SCORE
    # =====================================================

    def calculate_power_score(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities are not loaded."
            )

        scorer = PowerScore(
            self.facilities
        )

        self.facilities = (
            scorer.calculate()
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        if self.facilities is None:

            raise RuntimeError(
                "Nothing to save."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        geojson = (
            self.facilities.to_json()
        )

        with self.output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                geojson
            )

        print("--------------------------------")
        print(
            "Enriched dataset saved:"
        )

        print(
            self.output_file
        )