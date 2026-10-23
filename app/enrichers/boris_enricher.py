from __future__ import annotations

import json

import geopandas as gpd

from app.config.paths import DataPaths


class BorisEnricher:
    """
    Enriches DataCenterMap facilities with BORIS land values.

    Input:

        <run>/processed/datacentermap/facilities.geojson
        <run>/processed/boris/land_values.geojson

    Output:

        <run>/processed/enriched/facilities_land.geojson

    DataPaths controls the workspace so that the entire
    pipeline execution remains isolated.
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

        self.land_values_file = (
            self.paths.boris_processed
            / "land_values.geojson"
        )

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        self.output_dir = (
            self.paths.enriched
        )

        self.output_file = (
            self.output_dir
            / "facilities_land.geojson"
        )

        # -------------------------------------------------
        # Data
        # -------------------------------------------------

        self.facilities: (
            gpd.GeoDataFrame | None
        ) = None

        self.land_values: (
            gpd.GeoDataFrame | None
        ) = None

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def enrich(self):

        self.load_facilities()

        self.load_land_values()

        self.reproject()

        self.spatial_join()

        self.save()

        print("--------------------------------")
        print(
            "BORIS enrichment completed."
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
    # LOAD LAND VALUES
    # =====================================================

    def load_land_values(self):

        self.land_values = (
            self._read_geojson(
                self.land_values_file
            )
        )

        print("--------------------------------")
        print(
            f"Land Value Polygons : "
            f"{len(self.land_values)}"
        )

    # =====================================================
    # GEOJSON READER
    # =====================================================

    def _read_geojson(
        self,
        file_path,
    ) -> gpd.GeoDataFrame:
        """
        Read a generated GeoJSON dataset.

        Facilities are generated in WGS84.

        BORIS land values are generated in
        EPSG:25832 by BorisTransformer.
        """

        if not file_path.exists():

            raise FileNotFoundError(
                "GeoJSON file not found: "
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
        # Facilities
        # -------------------------------------------------

        if file_path == self.facilities_file:

            gdf = (
                gpd.GeoDataFrame.from_features(
                    features,
                    crs="EPSG:4326",
                )
            )

        # -------------------------------------------------
        # BORIS
        # -------------------------------------------------

        else:

            gdf = (
                gpd.GeoDataFrame.from_features(
                    features,
                    crs=self.TARGET_CRS,
                )
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

        if self.land_values is None:

            raise RuntimeError(
                "Land values have not "
                "been loaded."
            )

        self.facilities = (
            self.facilities.to_crs(
                epsg=25832
            )
        )

        self.land_values = (
            self.land_values.to_crs(
                epsg=25832
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
            f"BORIS CRS      : "
            f"{self.land_values.crs}"
        )

    # =====================================================
    # SPATIAL JOIN
    # =====================================================

    def spatial_join(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities have not "
                "been loaded."
            )

        if self.land_values is None:

            raise RuntimeError(
                "Land values have not "
                "been loaded."
            )

        print("--------------------------------")
        print(
            "Joining facilities with "
            "land value polygons..."
        )

        result = gpd.sjoin(
            self.facilities,
            self.land_values,
            how="left",
            predicate="within",
        )

        # -------------------------------------------------
        # Keep only one BORIS match per facility.
        # -------------------------------------------------

        result = (
            result
            .sort_index()
            .drop_duplicates(
                subset=[
                    "company",
                    "name",
                    "latitude",
                    "longitude",
                ],
                keep="first",
            )
            .reset_index(
                drop=True
            )
        )

        # -------------------------------------------------
        # Remove GeoPandas helper column.
        # -------------------------------------------------

        if "index_right" in result.columns:

            result.drop(
                columns=[
                    "index_right"
                ],
                inplace=True,
            )

        self.facilities = result

        print("--------------------------------")
        print(
            f"Matched Facilities : "
            f"{len(self.facilities)}"
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
            self.facilities.to_json(
                ensure_ascii=False
            )
        )

        self.output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")
        print(
            f"Saved : "
            f"{self.output_file}"
        )