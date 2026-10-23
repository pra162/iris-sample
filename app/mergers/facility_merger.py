from app.config.paths import DataPaths
from app.scrapers.datacentermap.facility_parser import (
    FacilityParser,
)


class FacilityMerger:
    """
    Merges all DataCenterMap facility files
    from the current pipeline workspace.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

    # =====================================================
    # MERGE
    # =====================================================

    def merge(self):

        parser = FacilityParser(
            paths=self.paths,
        )

        facility_dir = (
            self.paths.datacentermap_facilities_raw
        )

        if not facility_dir.exists():

            raise FileNotFoundError(
                "Facility raw directory not found: "
                f"{facility_dir}"
            )

        all_facilities = []

        files = sorted(
            facility_dir.glob("*.json")
        )

        print(
            f"Facility files found: "
            f"{len(files)}"
        )

        for file in files:

            slug = file.stem

            try:

                print(
                    f"Parsing {slug}"
                )

                facilities = parser.parse(
                    slug
                )

                all_facilities.extend(
                    facilities
                )

            except Exception as exc:

                print(
                    f"❌ Failed parsing "
                    f"{slug}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

        print(
            f"\nMerged "
            f"{len(all_facilities)} "
            f"facilities."
        )

        return all_facilities