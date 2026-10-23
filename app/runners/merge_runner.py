import json

from app.config.paths import DataPaths
from app.mergers.facility_merger import FacilityMerger


def run_merge(
    paths: DataPaths | None = None,
):
    """
    Merge all DataCenterMap facility data.

    When called from `all`, the runner receives the
    RunContext-specific DataPaths.

    When called independently, it remains backward
    compatible and uses the default `data/` paths.
    """

    paths = paths or DataPaths()

    merger = FacilityMerger(
        paths=paths,
    )

    facilities = merger.merge()

    output_dir = (
        paths.datacentermap_processed
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "facilities.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            facilities,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(facilities)} facilities "
        f"to {output_file}"
    )

    return facilities