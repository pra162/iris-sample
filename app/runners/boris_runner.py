from app.config.paths import DataPaths
from app.transformers.boris_transformer import (
    BorisTransformer,
)


class BorisRunner:
    """
    Runs the BORIS transformation pipeline.

    When called from `all`, the pipeline provides the
    current RunContext-specific DataPaths.

    When called independently, the default data/
    workspace is used.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):
        self.paths = paths or DataPaths()

    def run(self) -> None:

        transformer = BorisTransformer(
            paths=self.paths,
        )

        return transformer.transform()