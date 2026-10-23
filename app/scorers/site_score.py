from __future__ import annotations

import json

import geopandas as gpd

from app.config.paths import DataPaths


class SiteScore:
    """
    Calculates the unified site intelligence score.

    Inputs:

        <run>/processed/enriched/facilities_power.geojson
        <run>/processed/enriched/facilities_land.geojson

    Output:

        <run>/processed/enriched/facilities_site.geojson

    Site score:

        70% power readiness
        30% land value

    DataPaths controls the workspace so every pipeline
    execution remains isolated.
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

        self.power_file = (
            self.paths.enriched
            / "facilities_power.geojson"
        )

        self.land_file = (
            self.paths.enriched
            / "facilities_land.geojson"
        )

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        self.output_dir = (
            self.paths.enriched
        )

        self.output_file = (
            self.output_dir
            / "facilities_site.geojson"
        )

        # -------------------------------------------------
        # Data
        # -------------------------------------------------

        self.power: (
            gpd.GeoDataFrame | None
        ) = None

        self.land: (
            gpd.GeoDataFrame | None
        ) = None

        self.facilities: (
            gpd.GeoDataFrame | None
        ) = None

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def calculate(self):

        self.load()

        self.merge()

        self.calculate_land_score()

        self.calculate_site_score()

        self.rank()

        self.save()

        print("--------------------------------")
        print(
            "Site scoring completed."
        )

        return self.facilities

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        self.power = self._read_geojson(
            self.power_file,
            crs=self.TARGET_CRS,
        )

        self.land = self._read_geojson(
            self.land_file,
            crs=self.TARGET_CRS,
        )

        print("--------------------------------")
        print(
            f"Power Dataset : "
            f"{len(self.power)}"
        )

        print(
            f"Land Dataset  : "
            f"{len(self.land)}"
        )

    # =====================================================
    # GEOJSON READER
    # =====================================================

    def _read_geojson(
        self,
        file_path,
        crs: str,
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

        return (
            gpd.GeoDataFrame.from_features(
                features,
                crs=crs,
            )
        )

    # =====================================================
    # MERGE
    # =====================================================

    def merge(self):

        print("--------------------------------")
        print(
            "Merging datasets..."
        )

        if self.power is None:

            raise RuntimeError(
                "Power dataset has not "
                "been loaded."
            )

        if self.land is None:

            raise RuntimeError(
                "Land dataset has not "
                "been loaded."
            )

        land_columns = [
            "company",
            "name",
            "latitude",
            "longitude",
            "land_value_eur_m2",
            "municipality",
            "district",
        ]

        self.facilities = (
            self.power.merge(
                self.land[
                    land_columns
                ],
                on=[
                    "company",
                    "name",
                    "latitude",
                    "longitude",
                ],
                how="left",
                suffixes=(
                    "",
                    "_land",
                ),
            )
        )

        print(
            f"Merged Facilities : "
            f"{len(self.facilities)}"
        )

    # =====================================================
    # LAND SCORE
    # =====================================================

    def calculate_land_score(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities dataset has not "
                "been created."
            )

        print("--------------------------------")
        print(
            "Calculating Land Score..."
        )

        values = (
            self.facilities[
                "land_value_eur_m2"
            ]
        )

        minimum = values.min(
            skipna=True
        )

        maximum = values.max(
            skipna=True
        )

        # -------------------------------------------------
        # Avoid division by zero when all values
        # are identical.
        # -------------------------------------------------

        if minimum == maximum:

            self.facilities[
                "land_score"
            ] = 50.0

        else:

            self.facilities[
                "land_score"
            ] = (
                (
                    maximum
                    - values
                )
                /
                (
                    maximum
                    - minimum
                )
                * 100
            )

            self.facilities[
                "land_score"
            ] = (
                self.facilities[
                    "land_score"
                ]
                .fillna(50)
                .round(2)
            )

    # =====================================================
    # UNIFIED SITE SCORE
    # =====================================================

    def calculate_site_score(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities dataset has not "
                "been created."
            )

        print("--------------------------------")
        print(
            "Calculating Unified Site Score..."
        )

        self.facilities[
            "site_score"
        ] = (

            self.facilities[
                "power_readiness_score"
            ]
            * 0.70

            +

            self.facilities[
                "land_score"
            ]
            * 0.30

        ).round(2)

        self.facilities[
            "site_rating"
        ] = (
            self.facilities[
                "site_score"
            ]
            .apply(
                self.rating
            )
        )

    # =====================================================
    # RANK
    # =====================================================

    def rank(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities dataset has not "
                "been created."
            )

        self.facilities[
            "site_rank"
        ] = (

            self.facilities[
                "site_score"
            ]
            .rank(
                method="dense",
                ascending=False,
            )
            .astype(int)

        )

        print("--------------------------------")
        print(
            "Top 10 Sites"
        )

        print(
            self.facilities[
                [
                    "company",
                    "name",
                    "site_score",
                    "site_rating",
                    "site_rank",
                ]
            ]
            .sort_values(
                by="site_score",
                ascending=False,
            )
            .head(10)
            .to_string(
                index=False
            )
        )

    # =====================================================
    # RATING
    # =====================================================

    @staticmethod
    def rating(
        score: float,
    ) -> str:

        if score >= 90:
            return "Excellent"

        if score >= 75:
            return "Very Good"

        if score >= 60:
            return "Good"

        if score >= 40:
            return "Fair"

        return "Poor"

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
                ensure_ascii=False,
            )
        )

        self.output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")
        print(
            "Unified Site Intelligence Saved"
        )

        print(
            self.output_file
        )