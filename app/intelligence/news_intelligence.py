from __future__ import annotations

import json

import geopandas as gpd
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.paths import DataPaths
from app.database.models.news_match import NewsMatch
from app.database.models.news_article import NewsArticle


class NewsIntelligence:
    """
    Builds facility-level news intelligence.

    Input:
        - facilities_site.geojson
        - NewsMatch records from PostgreSQL

    Output:
        - facilities_intelligence.geojson

    News matches are linked to facilities using the business
    identity:

        company + facility_name

    We intentionally do not use GeoJSON properties["id"] because
    that ID is the original DataCenterMap facility ID, while
    NewsMatch.facility_id is the PostgreSQL UUID.

    DataPaths controls the filesystem workspace so the
    pipeline can run in an isolated run directory.
    """

    def __init__(
        self,
        session: Session,
        paths: DataPaths | None = None,
    ):

        self.session = session

        self.paths = paths or DataPaths()

        # --------------------------------------------------
        # Input
        # --------------------------------------------------

        self.facilities_file = (
            self.paths.enriched
            / "facilities_site.geojson"
        )

        # --------------------------------------------------
        # Output
        # --------------------------------------------------

        self.output_dir = (
            self.paths.intelligence
        )

        self.output_file = (
            self.output_dir
            / "facilities_intelligence.geojson"
        )

        # --------------------------------------------------
        # Data
        # --------------------------------------------------

        self.facilities: (
            gpd.GeoDataFrame | None
        ) = None

        self.matches: list[dict] = []

    # ========================================================
    # MAIN
    # ========================================================

    def build(self):

        self.load()

        self.aggregate_news()

        self.save()

        return self.facilities

    # ========================================================
    # LOAD
    # ========================================================

    def load(self):

        print("--------------------------------")
        print(
            "Loading Facilities..."
        )

        self.facilities = (
            self._read_geojson(
                self.facilities_file
            )
        )

        print(
            f"Facilities : "
            f"{len(self.facilities)}"
        )

        print("--------------------------------")
        print(
            "Loading News Intelligence "
            "from PostgreSQL..."
        )

        self.matches = (
            self._load_matches()
        )

        print(
            f"News Matches : "
            f"{len(self.matches)}"
        )

    # ========================================================
    # GEOJSON READER
    # ========================================================

    def _read_geojson(
        self,
        file_path,
    ) -> gpd.GeoDataFrame:

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

        return gpd.GeoDataFrame.from_features(
            features,
            crs="EPSG:4326",
        )

    # ========================================================
    # LOAD MATCHES FROM POSTGRESQL
    # ========================================================

    def _load_matches(self) -> list[dict]:

        rows = self.session.execute(

            select(
                NewsMatch.article_id,
                NewsMatch.facility_id,
                NewsMatch.company,
                NewsMatch.facility_name,
                NewsMatch.city,
                NewsMatch.match_type,
                NewsMatch.match_score,
                NewsArticle.published_at,
            )

            .join(
                NewsArticle,
                NewsArticle.id
                == NewsMatch.article_id,
            )

        ).all()

        matches = []

        for row in rows:

            matches.append(
                {
                    "article_id":
                        row.article_id,

                    "facility_id":
                        row.facility_id,

                    "company":
                        row.company,

                    "facility_name":
                        row.facility_name,

                    "city":
                        row.city,

                    "match_type":
                        row.match_type,

                    "match_score":
                        row.match_score,

                    "published_at":
                        row.published_at,
                }
            )

        return matches

    # ========================================================
    # NEWS AGGREGATION
    # ========================================================

    def aggregate_news(self):

        if self.facilities is None:

            raise RuntimeError(
                "Facilities have not been loaded."
            )

        print("--------------------------------")
        print(
            "Aggregating News Intelligence..."
        )

        # ----------------------------------------------------
        # No matches
        # ----------------------------------------------------

        if not self.matches:

            self.facilities[
                "news_count"
            ] = 0

            self.facilities[
                "match_score"
            ] = 0.0

            print("--------------------------------")
            print(
                "Facilities With News : 0"
            )

            return

        news_df = pd.DataFrame(
            self.matches
        )

        # ----------------------------------------------------
        # Normalize matching fields
        # ----------------------------------------------------

        news_df[
            "company_key"
        ] = (

            news_df[
                "company"
            ]

            .fillna("")

            .astype(str)

            .str.strip()

            .str.casefold()
        )

        news_df[
            "facility_name_key"
        ] = (

            news_df[
                "facility_name"
            ]

            .fillna("")

            .astype(str)

            .str.strip()

            .str.casefold()
        )

        # ----------------------------------------------------
        # Aggregate by company + facility name
        # ----------------------------------------------------

        grouped = (

            news_df

            .groupby(
                [
                    "company_key",
                    "facility_name_key",
                ],
                dropna=False,
            )

            .agg(

                news_count=(
                    "article_id",
                    "nunique",
                ),

                match_score=(
                    "match_score",
                    "mean",
                ),

            )

            .reset_index()

        )

        # ----------------------------------------------------
        # Create matching keys on facilities
        # ----------------------------------------------------

        self.facilities[
            "company_key"
        ] = (

            self.facilities[
                "company"
            ]

            .fillna("")

            .astype(str)

            .str.strip()

            .str.casefold()
        )

        self.facilities[
            "facility_name_key"
        ] = (

            self.facilities[
                "name"
            ]

            .fillna("")

            .astype(str)

            .str.strip()

            .str.casefold()
        )

        # ----------------------------------------------------
        # Merge
        # ----------------------------------------------------

        self.facilities = (
            self.facilities.merge(

                grouped,

                on=[
                    "company_key",
                    "facility_name_key",
                ],

                how="left",

                suffixes=(
                    "",
                    "_news",
                ),
            )
        )

        # ----------------------------------------------------
        # Normalize news_count
        # ----------------------------------------------------

        self.facilities[
            "news_count"
        ] = (

            self.facilities[
                "news_count"
            ]

            .fillna(0)

            .astype(int)
        )

        # ----------------------------------------------------
        # Normalize match_score
        # ----------------------------------------------------

        self.facilities[
            "match_score"
        ] = (

            self.facilities[
                "match_score"
            ]

            .fillna(0.0)

            .round(2)
        )

        # ----------------------------------------------------
        # Remove helper columns
        # ----------------------------------------------------

        self.facilities.drop(

            columns=[
                "company_key",
                "facility_name_key",
            ],

            inplace=True,

            errors="ignore",
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        facilities_with_news = (
            self.facilities[
                "news_count"
            ] > 0
        ).sum()

        print("--------------------------------")

        print(
            "Facilities With News : "
            f"{facilities_with_news}"
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(self):

        if self.facilities is None:

            raise RuntimeError(
                "Nothing to save."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        geojson = self.facilities.to_json(
            ensure_ascii=False,
        )

        self.output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")

        print(
            "News Intelligence Saved"
        )

        print(
            self.output_file
        )