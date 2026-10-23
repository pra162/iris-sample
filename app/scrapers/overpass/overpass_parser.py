import json

from app.config.paths import DataPaths


class OverpassParser:
    """
    Parses and merges Overpass raw JSON files.

    Input:
        <run>/raw/overpass/

        POWER:
            <country>_substations.json
            <country>_transformers.json
            <country>_power_lines.json

        TELECOM:
            <country>_telecom_lines.json
            <country>_telecom_points.json
            <country>_telecom_towers.json

    Output:
        <run>/raw/overpass/merged.json

    The workspace is controlled by DataPaths so that
    each pipeline execution remains isolated.
    """

    def __init__(
        self,
        paths: DataPaths | None = None,
        country_code: str = "DE",
    ):

        self.paths = paths or DataPaths()

        self.country_code = country_code.upper()

        self.input_dir = (
            self.paths.overpass_raw
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
                f"Overpass raw directory not found: "
                f"{self.input_dir}"
            )

        country = self.country_code.lower()

        # -------------------------------------------------
        # POWER FILES
        # -------------------------------------------------

        power_files = [

            self.input_dir
            / f"{country}_substations.json",

            self.input_dir
            / f"{country}_transformers.json",

            self.input_dir
            / f"{country}_power_lines.json",
        ]

        # -------------------------------------------------
        # TELECOM FILES
        # -------------------------------------------------

        telecom_files = [

            self.input_dir
            / f"{country}_telecom_lines.json",

            self.input_dir
            / f"{country}_telecom_points.json",

            self.input_dir
            / f"{country}_telecom_towers.json",
        ]

        # -------------------------------------------------
        # ALL INPUT FILES
        # -------------------------------------------------

        input_files = (
            power_files
            + telecom_files
        )

        existing_files = [
            file
            for file in input_files
            if file.exists()
        ]

        if not existing_files:

            raise FileNotFoundError(
                "No Overpass data files found "
                f"in {self.input_dir}."
            )

        merged_elements = []

        seen = set()

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------

        statistics = {
            "power": {
                "substations": 0,
                "transformers": 0,
                "power_lines": 0,
            },

            "telecom": {
                "telecom_lines": 0,
                "telecom_points": 0,
                "telecom_towers": 0,
            },
        }

        # -------------------------------------------------
        # Read each Overpass response
        # -------------------------------------------------

        for input_file in existing_files:

            print(
                "Reading "
                f"{input_file.name}"
            )

            with input_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            elements = data.get(
                "elements",
                [],
            )

            print(
                f"Elements : "
                f"{len(elements)}"
            )

            # -------------------------------------------------
            # Determine dataset
            # -------------------------------------------------

            dataset_name = (
                input_file.stem
                .replace(
                    f"{country}_",
                    "",
                    1,
                )
            )

            # -------------------------------------------------
            # Merge elements
            # -------------------------------------------------

            for element in elements:

                element_type = element.get(
                    "type"
                )

                element_id = element.get(
                    "id"
                )

                if (
                    element_type is None
                    or element_id is None
                ):

                    continue

                key = (
                    element_type,
                    element_id,
                )

                if key in seen:

                    continue

                seen.add(key)

                merged_elements.append(
                    element
                )

                # -------------------------------------------------
                # Statistics
                # -------------------------------------------------

                if dataset_name in statistics[
                    "power"
                ]:

                    statistics[
                        "power"
                    ][dataset_name] += 1

                elif dataset_name in statistics[
                    "telecom"
                ]:

                    statistics[
                        "telecom"
                    ][dataset_name] += 1

        # -------------------------------------------------
        # Build merged result
        # -------------------------------------------------

        result = {

            "country_code":
                self.country_code,

            "elements":
                merged_elements,

            "statistics":
                statistics,
        }

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                result,
                file,
                ensure_ascii=False,
                indent=2,
            )

        # -------------------------------------------------
        # Output summary
        # -------------------------------------------------

        print("--------------------------------")

        print(
            f"Input Files     : "
            f"{len(existing_files)}"
        )

        print(
            "Power:"
        )

        print(
            "  Substations    : "
            f"{statistics['power']['substations']}"
        )

        print(
            "  Transformers   : "
            f"{statistics['power']['transformers']}"
        )

        print(
            "  Power Lines    : "
            f"{statistics['power']['power_lines']}"
        )

        print(
            "Telecom:"
        )

        print(
            "  Telecom Lines  : "
            f"{statistics['telecom']['telecom_lines']}"
        )

        print(
            "  Telecom Points : "
            f"{statistics['telecom']['telecom_points']}"
        )

        print(
            "  Telecom Towers : "
            f"{statistics['telecom']['telecom_towers']}"
        )

        print(
            f"Unique Elements : "
            f"{len(merged_elements)}"
        )

        print(
            f"Saved           : "
            f"{self.output_file}"
        )

        return result