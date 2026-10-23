from app.config.paths import DataPaths

from app.news.rss_fetcher import RSSFetcher
from app.news.article_parser import ArticleParser
from app.news.entity_extractor import EntityExtractor


def run(
    paths: DataPaths | None = None,
):
    """
    Run the complete news acquisition and extraction pipeline.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    fetcher = RSSFetcher(
        paths=paths,
    )

    fetcher.fetch()

    parser = ArticleParser(
        paths=paths,
    )

    parser.parse()

    extractor = EntityExtractor(
        paths=paths,
    )

    extractor.extract()