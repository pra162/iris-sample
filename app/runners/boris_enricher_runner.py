from app.config.paths import DataPaths
from app.enrichers.boris_enricher import BorisEnricher


def run(
    paths: DataPaths | None = None,
):
    """
    Run the BORIS enrichment stage.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    enricher = BorisEnricher(
        paths=paths,
    )

    return enricher.enrich()