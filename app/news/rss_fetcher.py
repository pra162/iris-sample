from __future__ import annotations

import json

import feedparser

from app.config.data_sources import get_data_source
from app.config.paths import DataPaths


class RSSFetcher:
    """
    Downloads RSS feeds from configured news sources
    and stores the raw articles as JSON.

    Responsibilities:
    - Fetch RSS feeds
    - Normalize feed metadata
    - Save raw news articles

    The output workspace is controlled by DataPaths
    so each pipeline execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        self.output_dir = (
            self.paths.news_raw
        )

        self.output_file = (
            self.output_dir
            / "news_raw.json"
        )

        # -------------------------------------------------
        # Data source
        # -------------------------------------------------

        self.source = get_data_source(
            "news_datacenter_insider"
        )

    # =====================================================
    # FETCH
    # =====================================================

    def fetch(self):

        if not self.source.urls:

            raise ValueError(
                "No RSS URL configured for "
                f"{self.source.name}."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        articles = []

        print("--------------------------------")
        print(
            "Fetching RSS feeds..."
        )

        for url in self.source.urls:

            print(
                f"Source : "
                f"{self.source.name}"
            )

            feed = feedparser.parse(
                url
            )

            print(
                f"Articles Found : "
                f"{len(feed.entries)}"
            )

            for entry in feed.entries:

                articles.append(
                    {
                        "source": (
                            self.source.name
                        ),
                        "title": (
                            entry.get(
                                "title"
                            )
                        ),
                        "link": (
                            entry.get(
                                "link"
                            )
                        ),
                        "published": (
                            entry.get(
                                "published"
                            )
                        ),
                        "summary": (
                            entry.get(
                                "summary"
                            )
                        ),
                    }
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
            f"Saved {len(articles)} articles"
        )

        print(
            self.output_file
        )

        return articles