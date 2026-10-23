from app.config.paths import DataPaths
from app.news.entity_matcher import EntityMatcher


def run(
    paths: DataPaths | None = None,
):
    """
    Run news entity matching.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    matcher = EntityMatcher(
        paths=paths,
    )

    return matcher.match()