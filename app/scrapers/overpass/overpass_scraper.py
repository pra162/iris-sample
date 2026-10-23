import json
import logging

from app.config.data_sources import get_country_config
from app.config.data_sources import get_data_source
from app.config.paths import DataPaths
from app.scrapers.base.http_client import HttpClient


logger = logging.getLogger(__name__)


class OverpassScraper:
    """
    Scrapes OpenStreetMap infrastructure data
    through the Overpass API.

    Currently collects:

        POWER
        - Substations
        - Transformers
        - Power transmission lines

        TELECOM
        - Fibre / telecom paths
        - Communication lines
        - Telecom exchanges
        - Telecom connection points
        - Telecom distribution points
        - Telecom service devices
        - Internet exchanges
        - Data centres
        - Telecom masts / towers

    All output paths are controlled by DataPaths.

    If the Overpass API is temporarily unavailable but
    a previously downloaded dataset exists locally, the
    cached dataset is retained and the pipeline continues.
    """

    def __init__(
        self,
        country_code: str = "DE",
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        self.http_client = HttpClient()

        self.country_code = (
            country_code.upper()
        )

        self.source = get_data_source(
            "overpass"
        )

        self.country = get_country_config(
            self.country_code
        )

        # -------------------------------------------------
        # Run-specific output directory
        # -------------------------------------------------

        self.output_dir = (
            self.paths.overpass_raw
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # MAIN SCRAPER
    # =====================================================

    def scrape(self):

        if not self.source.urls:

            raise ValueError(
                "No URL configured for Overpass data source."
            )

        print(
            f"Country : "
            f"{self.country_code}"
        )

        print(
            "Building Overpass queries..."
        )

        queries = {

            # -------------------------------------------------
            # POWER
            # -------------------------------------------------

            "substations": (
                self.build_substation_query()
            ),

            "transformers": (
                self.build_transformer_query()
            ),

            "power_lines": (
                self.build_power_line_query()
            ),

            # -------------------------------------------------
            # TELECOM
            # -------------------------------------------------

            "telecom_lines": (
                self.build_telecom_line_query()
            ),

            "telecom_points": (
                self.build_telecom_point_query()
            ),

            "telecom_towers": (
                self.build_telecom_tower_query()
            ),
        }

        for name, query in queries.items():

            self._run_query(
                name=name,
                query=query,
            )

        print("--------------------------------")
        print(
            "Overpass scraping completed."
        )

    # =====================================================
    # QUERY EXECUTION
    # =====================================================

    def _run_query(
        self,
        name: str,
        query: str,
    ):

        print("--------------------------------")

        print(
            f"Downloading {name}..."
        )

        output_file = (
            self.output_dir
            / (
                f"{self.country_code.lower()}_"
                f"{name}.json"
            )
        )

        try:

            response = self.http_client.post(
                self.source.urls[0],
                data={
                    "data": query,
                },
                headers={
                    "Accept": "application/json",
                },
            )

            data = response.json()

            if not isinstance(
                data,
                dict,
            ):

                raise ValueError(
                    "Overpass response is not a JSON object."
                )

            elements = data.get(
                "elements",
                [],
            )

            if not isinstance(
                elements,
                list,
            ):

                raise ValueError(
                    "Overpass response does not contain "
                    "a valid elements list."
                )

            # -------------------------------------------------
            # Save fresh dataset
            # -------------------------------------------------

            with output_file.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                f"Elements : "
                f"{len(elements)}"
            )

            print(
                f"Saved    : "
                f"{output_file}"
            )

            return

        except Exception as exc:

            # -------------------------------------------------
            # Cached dataset fallback
            # -------------------------------------------------

            if output_file.exists():

                try:

                    with output_file.open(
                        "r",
                        encoding="utf-8",
                    ) as file:

                        cached_data = json.load(
                            file
                        )

                    cached_elements = (
                        cached_data.get(
                            "elements",
                            [],
                        )
                    )

                    if not isinstance(
                        cached_elements,
                        list,
                    ):

                        raise ValueError(
                            "Cached dataset does not contain "
                            "a valid elements list."
                        )

                    print(
                        f"Overpass request failed for "
                        f"{name}: {exc}"
                    )

                    print(
                        "Using cached dataset:"
                    )

                    print(
                        f"Elements : "
                        f"{len(cached_elements)}"
                    )

                    print(
                        f"Cached   : "
                        f"{output_file}"
                    )

                    logger.warning(
                        "Overpass request failed for %s. "
                        "Using cached dataset %s. Error: %s",
                        name,
                        output_file,
                        exc,
                    )

                    return

                except Exception as cache_exc:

                    raise RuntimeError(
                        f"Overpass request failed for "
                        f"{name}, and the cached dataset "
                        f"could not be used: "
                        f"{cache_exc}"
                    ) from exc

            # -------------------------------------------------
            # No cached dataset
            # -------------------------------------------------

            raise RuntimeError(
                f"Overpass request failed for "
                f"{name}, and no cached dataset "
                f"exists at {output_file}."
            ) from exc

    # =====================================================
    # POWER
    # =====================================================

    # -----------------------------------------------------
    # SUBSTATIONS
    # -----------------------------------------------------

    def build_substation_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:120];

(
  node["power"="substation"]({bbox});
  way["power"="substation"]({bbox});
  relation["power"="substation"]({bbox});
);

out body;
>;
out skel qt;
"""

    # -----------------------------------------------------
    # TRANSFORMERS
    # -----------------------------------------------------

    def build_transformer_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:120];

(
  node["power"="transformer"]({bbox});
  way["power"="transformer"]({bbox});
);

out body;
>;
out skel qt;
"""

    # -----------------------------------------------------
    # POWER LINES
    # -----------------------------------------------------

    def build_power_line_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:120];

way["power"="line"]({bbox});

out body;
>;
out skel qt;
"""

    # =====================================================
    # TELECOM
    # =====================================================

    # -----------------------------------------------------
    # TELECOM / FIBRE LINES
    # -----------------------------------------------------

    def build_telecom_line_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:180];

(
  way["telecom"="path"]({bbox});

  way["communication"="line"]({bbox});

  way["telecom"="line"]({bbox});

  way["telecom:medium"="fibre"]({bbox});

  way["utility"="telecom"]({bbox});
);

out body;
>;
out skel qt;
"""

    # -----------------------------------------------------
    # TELECOM POINTS
    # -----------------------------------------------------

    def build_telecom_point_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:180];

(
  node["telecom"="exchange"]({bbox});
  way["telecom"="exchange"]({bbox});
  relation["telecom"="exchange"]({bbox});

  node["telecom"="connection_point"]({bbox});
  way["telecom"="connection_point"]({bbox});
  relation["telecom"="connection_point"]({bbox});

  node["telecom"="distribution_point"]({bbox});
  way["telecom"="distribution_point"]({bbox});
  relation["telecom"="distribution_point"]({bbox});

  node["telecom"="service_device"]({bbox});
  way["telecom"="service_device"]({bbox});
  relation["telecom"="service_device"]({bbox});

  node["telecom"="internet_exchange"]({bbox});
  way["telecom"="internet_exchange"]({bbox});
  relation["telecom"="internet_exchange"]({bbox});

  node["telecom"="data_center"]({bbox});
  way["telecom"="data_center"]({bbox});
  relation["telecom"="data_center"]({bbox});
);

out body;
>;
out skel qt;
"""

    # -----------------------------------------------------
    # TELECOM TOWERS / MASTS
    # -----------------------------------------------------

    def build_telecom_tower_query(
        self,
    ):

        bbox = (
            self.country.overpass_bbox
        )

        return f"""
[out:json][timeout:180];

(
  node["man_made"="communications_tower"]({bbox});
  way["man_made"="communications_tower"]({bbox});
  relation["man_made"="communications_tower"]({bbox});

  node["man_made"="mast"]["tower:type"="communication"]({bbox});
  way["man_made"="mast"]["tower:type"="communication"]({bbox});

  node["man_made"="tower"]["tower:type"="communication"]({bbox});
  way["man_made"="tower"]["tower:type"="communication"]({bbox});
);

out body;
>;
out skel qt;
"""