from __future__ import annotations

import json
import uuid

from app.config.paths import DataPaths


class ArticleParser:
    """
    Normalizes raw RSS articles into a common format
    used by the News Intelligence pipeline.

    Input:

        <run>/raw/news/news_raw.json

    Output:

        <run>/processed/news/news.json

    DataPaths controls the workspace so each pipeline
    execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        self.input_file = (
            self.paths.news_raw
            / "news_raw.json"
        )

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        self.output_dir = (
            self.paths.news_processed
        )

        self.output_file = (
            self.output_dir
            / "news.json"
        )

    # =====================================================
    # PARSE
    # =====================================================

    def parse(self):

        print("--------------------------------")
        print(
            "Parsing news articles..."
        )

        if not self.input_file.exists():

            raise FileNotFoundError(
                "News raw input file not found: "
                f"{self.input_file}"
            )

        with self.input_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            raw_articles = json.load(
                file
            )

        if not isinstance(
            raw_articles,
            list,
        ):

            raise ValueError(
                "Expected news raw data "
                "to contain a list."
            )

        articles = []

        for article in raw_articles:

            articles.append(
                {
                    "id": str(
                        uuid.uuid4()
                    ),

                    "source": (
                        article.get(
                            "source"
                        )
                    ),

                    "title": (
                        article.get(
                            "title"
                        )
                    ),

                    "summary": (
                        article.get(
                            "summary"
                        )
                    ),

                    "url": (
                        article.get(
                            "link"
                        )
                    ),

                    "published": (
                        article.get(
                            "published"
                        )
                    ),

                    "language": "de",

                    "processed": False,
                }
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                articles,
                file,
                indent=4,
                ensure_ascii=False,
            )

        print("--------------------------------")
        print(
            f"Normalized Articles : "
            f"{len(articles)}"
        )

        print(
            self.output_file
        )

        return articles