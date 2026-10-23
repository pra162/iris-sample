from app.config.paths import DataPaths
from app.scorers.site_score import SiteScore


def run(
    paths: DataPaths | None = None,
):
    """
    Run the site scoring stage.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    scorer = SiteScore(
        paths=paths,
    )

    return scorer.calculate()