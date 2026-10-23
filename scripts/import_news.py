"""
Import News Intelligence

Imports processed news articles and entity matches
into PostgreSQL.

Author:
NRW BI Platform
"""

from __future__ import annotations

import json

from pathlib import Path
from email.utils import parsedate_to_datetime

from sqlalchemy import select

from app.database.session import SessionLocal

from app.database.models.news_article import NewsArticle
from app.database.models.news_match import NewsMatch
from app.database.models.facility import Facility


# ==========================================================
# Paths
# ==========================================================

BASE_PATH = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "data"
    / "processed"
    / "news"
)

NEWS_FILE = BASE_PATH / "news.json"

MATCH_FILE = BASE_PATH / "matched_news.json"


# ==========================================================
# Helpers
# ==========================================================


def load_json(path: Path):

    if not path.exists():
        raise FileNotFoundError(path)

    with open(
        path,
        encoding="utf-8",
    ) as f:

        return json.load(f)


def parse_date(value: str | None):

    if not value:
        return None

    try:
        return parsedate_to_datetime(value)

    except Exception:
        return None


# ==========================================================
# Import Articles
# ==========================================================


def import_articles(session) -> int:

    articles = load_json(NEWS_FILE)

    imported = 0

    for article in articles:

        existing = session.get(
            NewsArticle,
            article["id"],
        )

        if existing:
            continue

        news = NewsArticle(

            id=article["id"],

            source=article.get("source"),

            title=article.get("title"),

            summary=article.get("summary"),

            url=article.get("url"),

            language=article.get(
                "language",
                "en",
            ),

            processed=article.get(
                "processed",
                False,
            ),

            published_at=parse_date(
                article.get("published"),
            ),
        )

        session.add(news)

        imported += 1

    session.commit()

    return imported


# ==========================================================
# Import Matches
# ==========================================================


def import_matches(session) -> int:

    matches = load_json(MATCH_FILE)

    imported = 0

    for row in matches:

        existing = session.execute(

            select(NewsMatch).where(

                NewsMatch.article_id == row["article_id"],

                NewsMatch.company == row["company"],

                NewsMatch.facility_name == row["facility_name"],
            )

        ).scalar_one_or_none()

        if existing:
            continue

        facility = session.execute(

            select(Facility).where(

                Facility.company == row["company"],

                Facility.name == row["facility_name"],
            )

        ).scalar_one_or_none()

        if facility is None:

            facility = session.execute(

                select(Facility).where(

                    Facility.company == row["company"]
                )

            ).scalar_one_or_none()

        match = NewsMatch(

            article_id=row["article_id"],

            facility_id=(
                facility.id
                if facility
                else None
            ),

            company=row.get("company"),

            facility_name=row.get(
                "facility_name"
            ),

            city=row.get("city"),

            match_type=row.get(
                "match_type"
            ),

            match_score=row.get(
                "match_score",
                0.0,
            ),
        )

        session.add(match)

        imported += 1

    session.commit()

    return imported


# ==========================================================
# Main
# ==========================================================


def main():

    session = SessionLocal()

    try:

        print()

        print("=" * 60)
        print("NEWS INTELLIGENCE IMPORT")
        print("=" * 60)

        article_count = import_articles(
            session
        )

        match_count = import_matches(
            session
        )

        print()

        print(
            f"✓ Imported Articles : {article_count}"
        )

        print(
            f"✓ Imported Matches  : {match_count}"
        )

        print()

        print(
            "News Intelligence successfully imported."
        )

        print("=" * 60)

    finally:

        session.close()


# ==========================================================

if __name__ == "__main__":

    main()