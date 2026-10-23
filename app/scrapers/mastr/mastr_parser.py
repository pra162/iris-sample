import json

from app.config.paths import DataPaths


class MaStRParser:
    """
    Parses and merges MaStR raw page responses.

    Input:
        <run>/raw/mastr/page_*.json

    Output:
        <run>/raw/mastr/merged.json

    The workspace is controlled by DataPaths so that
    each pipeline execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # -------------------------------------------------
        # Run-specific paths
        # -------------------------------------------------

        self.input_dir = (
            self.paths.mastr_raw
        )

        self.output_file = (
            self.input_dir
            / "merged.json"
        )

    # =====================================================
    # PARSE
    # =====================================================

    def parse(self):

        if not self.input_dir.exists():

            raise FileNotFoundError(
                f"MaStR raw directory not found: "
                f"{self.input_dir}"
            )

        merged_records = []

        page_files = sorted(
            self.input_dir.glob(
                "page_*.json"
            )
        )

        if not page_files:

            raise FileNotFoundError(
                "No MaStR page files found "
                f"in {self.input_dir}."
            )

        print(
            f"Found {len(page_files)} "
            f"MaStR page(s)."
        )

        for page_file in page_files:

            print(
                f"Reading "
                f"{page_file.name}"
            )

            with page_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            records = data.get(
                "Data",
                [],
            )

            if not isinstance(
                records,
                list,
            ):

                print(
                    f"⚠ {page_file.name}: "
                    "Data is not a list. "
                    "Skipping."
                )

                continue

            merged_records.extend(
                records
            )

        with self.output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                merged_records,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print("--------------------------------")
        print(
            f"Total Records : "
            f"{len(merged_records)}"
        )

        print(
            f"Saved         : "
            f"{self.output_file}"
        )

        return merged_records