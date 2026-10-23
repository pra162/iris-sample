from app.config.paths import DataPaths
from app.enrichers.power_enricher import PowerEnricher


def run(
    paths: DataPaths | None = None,
):
    """
    Run the power infrastructure enrichment.

    When called from `all`, the current RunContext-specific
    DataPaths are provided.

    When called independently, the default data/
    workspace is used.
    """

    paths = paths or DataPaths()

    enricher = PowerEnricher(
        paths=paths,
    )

    return enricher.enrich()