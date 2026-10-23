from __future__ import annotations

import json

import geopandas as gpd
from shapely.geometry import LineString
from shapely.geometry import Point

from app.config.paths import DataPaths


class OverpassTransformer:
    """
    Transforms merged Overpass data into separate GeoJSON
    representations for power and telecom infrastructure.

    Input:
        <run>/raw/overpass/merged.json

    Outputs:
        <run>/processed/overpass/power_grid.geojson
        <run>/processed/overpass/telecom_network.geojson

    Power infrastructure:
        - Substations
        - Transformers
        - Power lines

    Telecom infrastructure:
        - Fibre paths
        - Communication lines
        - Telecom lines
        - Telecom exchanges
        - Connection points
        - Distribution points
        - Telecom service devices
        - Internet exchanges
        - Telecom data centres
        - Communication towers
        - Communication masts

    The paths are controlled by DataPaths so each
    pipeline execution can use an isolated workspace.
    """

    CRS = "EPSG:4326"

    # =====================================================
    # TELECOM TYPES
    # =====================================================

    TELECOM_LINE_TYPES = {
        "telecom_path",
        "communication_line",
        "telecom_line",
        "fibre",
        "telecom_utility",
    }

    TELECOM_POINT_TYPES = {
        "exchange",
        "connection_point",
        "distribution_point",
        "service_device",
        "internet_exchange",
        "data_center",
        "communications_tower",
        "communication_mast",
        "communication_tower",
    }

    def __init__(
        self,
        paths: DataPaths | None = None,
    ):

        self.paths = paths or DataPaths()

        # -------------------------------------------------
        # Run-specific paths
        # -------------------------------------------------

        self.input_file = (
            self.paths.overpass_raw
            / "merged.json"
        )

        self.output_dir = (
            self.paths.overpass_processed
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # Power output
        # -------------------------------------------------

        self.power_output_file = (
            self.output_dir
            / "power_grid.geojson"
        )

        # -------------------------------------------------
        # Telecom output
        # -------------------------------------------------

        self.telecom_output_file = (
            self.output_dir
            / "telecom_network.geojson"
        )

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        self.elements = []

        # -------------------------------------------------
        # Node lookup
        #
        # Used to reconstruct OSM ways.
        # -------------------------------------------------

        self.node_lookup = {}

        # -------------------------------------------------
        # Power features
        # -------------------------------------------------

        self.power_features = []

        # -------------------------------------------------
        # Telecom features
        # -------------------------------------------------

        self.telecom_features = []

        # -------------------------------------------------
        # GeoDataFrames
        # -------------------------------------------------

        self.power_gdf: gpd.GeoDataFrame | None = None

        self.telecom_gdf: gpd.GeoDataFrame | None = None

        # -------------------------------------------------
        # Backwards compatibility
        #
        # Existing code may still expect:
        #
        # transformer.features
        # transformer.gdf
        #
        # Keep these aliases pointing to the power output.
        # -------------------------------------------------

        self.features = self.power_features

        self.gdf: gpd.GeoDataFrame | None = None

    # =====================================================
    # TRANSFORM
    # =====================================================

    def transform(self):

        self.load_elements()

        self.build_node_lookup()

        # -------------------------------------------------
        # POWER
        # -------------------------------------------------

        self.transform_power_nodes()

        self.transform_power_ways()

        self.create_power_geodataframe()

        self.save_power_geojson()

        # -------------------------------------------------
        # TELECOM
        # -------------------------------------------------

        self.transform_telecom_nodes()

        self.transform_telecom_ways()

        self.create_telecom_geodataframe()

        self.save_telecom_geojson()

        # -------------------------------------------------
        # Backwards compatibility
        # -------------------------------------------------

        self.features = self.power_features

        self.gdf = self.power_gdf

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        print("--------------------------------")
        print(
            "Overpass transformation completed."
        )

        print("--------------------------------")
        print(
            f"Power Features   : "
            f"{len(self.power_features)}"
        )

        print(
            f"Telecom Features : "
            f"{len(self.telecom_features)}"
        )

        print("--------------------------------")

        return {
            "power": self.power_gdf,
            "telecom": self.telecom_gdf,
        }

    # =====================================================
    # LOAD ELEMENTS
    # =====================================================

    def load_elements(self):

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"Overpass input file not found: "
                f"{self.input_file}"
            )

        with self.input_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "Expected Overpass merged JSON "
                "to contain an object."
            )

        self.elements = data.get(
            "elements",
            [],
        )

        print("--------------------------------")

        print(
            f"Loaded Elements : "
            f"{len(self.elements)}"
        )

    # =====================================================
    # NODE LOOKUP
    # =====================================================

    def build_node_lookup(self):

        self.node_lookup = {}

        for element in self.elements:

            if element.get("type") != "node":

                continue

            element_id = element.get(
                "id"
            )

            longitude = element.get(
                "lon"
            )

            latitude = element.get(
                "lat"
            )

            if (
                element_id is None
                or longitude is None
                or latitude is None
            ):

                continue

            self.node_lookup[element_id] = (
                longitude,
                latitude,
            )

        print(
            f"Node Lookup Size : "
            f"{len(self.node_lookup)}"
        )

    # =====================================================
    # POWER
    # =====================================================

    # -----------------------------------------------------
    # POWER NODES
    # -----------------------------------------------------

    def transform_power_nodes(self):

        count = 0

        for element in self.elements:

            if element.get("type") != "node":

                continue

            tags = element.get(
                "tags",
                {},
            )

            if "power" not in tags:

                continue

            longitude = element.get(
                "lon"
            )

            latitude = element.get(
                "lat"
            )

            if (
                longitude is None
                or latitude is None
            ):

                continue

            feature = {
                "source": "osm",

                "osm_id": element.get(
                    "id"
                ),

                "element_type": "node",

                "power_type": tags.get(
                    "power"
                ),

                "name": tags.get(
                    "name"
                ),

                "operator": tags.get(
                    "operator"
                ),

                "voltage": tags.get(
                    "voltage"
                ),

                "frequency": tags.get(
                    "frequency"
                ),

                "reference": tags.get(
                    "ref"
                ),

                "geometry": Point(
                    longitude,
                    latitude,
                ),
            }

            self.power_features.append(
                feature
            )

            count += 1

        print(
            f"Power Node Features : "
            f"{count}"
        )

    # -----------------------------------------------------
    # POWER WAYS
    # -----------------------------------------------------

    def transform_power_ways(self):

        count = 0

        for element in self.elements:

            if element.get("type") != "way":

                continue

            tags = element.get(
                "tags",
                {},
            )

            if "power" not in tags:

                continue

            coordinates = []

            for node_id in element.get(
                "nodes",
                [],
            ):

                point = self.node_lookup.get(
                    node_id
                )

                if point:

                    coordinates.append(
                        point
                    )

            # A LineString requires at least
            # two coordinate points.

            if len(coordinates) < 2:

                continue

            feature = {
                "source": "osm",

                "osm_id": element.get(
                    "id"
                ),

                "element_type": "way",

                "power_type": tags.get(
                    "power"
                ),

                "name": tags.get(
                    "name"
                ),

                "operator": tags.get(
                    "operator"
                ),

                "voltage": tags.get(
                    "voltage"
                ),

                "frequency": tags.get(
                    "frequency"
                ),

                "reference": tags.get(
                    "ref"
                ),

                "geometry": LineString(
                    coordinates
                ),
            }

            self.power_features.append(
                feature
            )

            count += 1

        print(
            f"Power Way Features : "
            f"{count}"
        )

    # =====================================================
    # TELECOM
    # =====================================================

    # -----------------------------------------------------
    # TELECOM TYPE DETECTION
    # -----------------------------------------------------

    @staticmethod
    def classify_telecom(
        tags: dict,
    ) -> str | None:
        """
        Determines the logical telecom infrastructure type
        from OSM tags.

        Returns:
            A normalized telecom type or None.
        """

        telecom = (
            tags.get("telecom")
            or ""
        ).lower()

        communication = (
            tags.get("communication")
            or ""
        ).lower()

        telecom_medium = (
            tags.get("telecom:medium")
            or ""
        ).lower()

        utility = (
            tags.get("utility")
            or ""
        ).lower()

        man_made = (
            tags.get("man_made")
            or ""
        ).lower()

        tower_type = (
            tags.get("tower:type")
            or ""
        ).lower()

        # -------------------------------------------------
        # Fibre
        # -------------------------------------------------

        if (
            telecom_medium == "fibre"
        ):

            return "fibre"

        # -------------------------------------------------
        # Telecom path
        # -------------------------------------------------

        if telecom == "path":

            return "telecom_path"

        # -------------------------------------------------
        # Communication line
        # -------------------------------------------------

        if communication == "line":

            return "communication_line"

        # -------------------------------------------------
        # Telecom line
        # -------------------------------------------------

        if telecom == "line":

            return "telecom_line"

        # -------------------------------------------------
        # Telecom utility
        # -------------------------------------------------

        if utility == "telecom":

            return "telecom_utility"

        # -------------------------------------------------
        # Exchange
        # -------------------------------------------------

        if telecom == "exchange":

            return "exchange"

        # -------------------------------------------------
        # Connection point
        # -------------------------------------------------

        if telecom == "connection_point":

            return "connection_point"

        # -------------------------------------------------
        # Distribution point
        # -------------------------------------------------

        if telecom == "distribution_point":

            return "distribution_point"

        # -------------------------------------------------
        # Service device
        # -------------------------------------------------

        if telecom == "service_device":

            return "service_device"

        # -------------------------------------------------
        # Internet exchange
        # -------------------------------------------------

        if telecom == "internet_exchange":

            return "internet_exchange"

        # -------------------------------------------------
        # Data centre
        # -------------------------------------------------

        if telecom in {
            "data_center",
            "data_centre",
        }:

            return "data_center"

        # -------------------------------------------------
        # Communication towers
        # -------------------------------------------------

        if (
            man_made
            == "communications_tower"
        ):

            return "communications_tower"

        # -------------------------------------------------
        # Communication mast
        # -------------------------------------------------

        if (
            man_made == "mast"
            and tower_type
            == "communication"
        ):

            return "communication_mast"

        # -------------------------------------------------
        # Communication tower
        # -------------------------------------------------

        if (
            man_made == "tower"
            and tower_type
            == "communication"
        ):

            return "communication_tower"

        return None

    # -----------------------------------------------------
    # TELECOM NODES
    # -----------------------------------------------------

    def transform_telecom_nodes(self):

        count = 0

        for element in self.elements:

            if element.get("type") != "node":

                continue

            tags = element.get(
                "tags",
                {},
            )

            telecom_type = (
                self.classify_telecom(
                    tags
                )
            )

            if telecom_type is None:

                continue

            longitude = element.get(
                "lon"
            )

            latitude = element.get(
                "lat"
            )

            if (
                longitude is None
                or latitude is None
            ):

                continue

            feature = {
                "source": "osm",

                "osm_id": element.get(
                    "id"
                ),

                "element_type": "node",

                "telecom_type":
                    telecom_type,

                "name": tags.get(
                    "name"
                ),

                "operator": tags.get(
                    "operator"
                ),

                "reference": tags.get(
                    "ref"
                ),

                "technology": tags.get(
                    "telecom"
                ),

                "medium": tags.get(
                    "telecom:medium"
                ),

                "connection_type": tags.get(
                    "connection"
                ),

                "capacity": tags.get(
                    "capacity"
                ),

                "geometry": Point(
                    longitude,
                    latitude,
                ),
            }

            self.telecom_features.append(
                feature
            )

            count += 1

        print(
            f"Telecom Node Features : "
            f"{count}"
        )

    # -----------------------------------------------------
    # TELECOM WAYS
    # -----------------------------------------------------

    def transform_telecom_ways(self):

        count = 0

        for element in self.elements:

            if element.get("type") != "way":

                continue

            tags = element.get(
                "tags",
                {},
            )

            telecom_type = (
                self.classify_telecom(
                    tags
                )
            )

            if telecom_type is None:

                continue

            coordinates = []

            for node_id in element.get(
                "nodes",
                [],
            ):

                point = self.node_lookup.get(
                    node_id
                )

                if point:

                    coordinates.append(
                        point
                    )

            if len(coordinates) < 2:

                continue

            feature = {
                "source": "osm",

                "osm_id": element.get(
                    "id"
                ),

                "element_type": "way",

                "telecom_type":
                    telecom_type,

                "name": tags.get(
                    "name"
                ),

                "operator": tags.get(
                    "operator"
                ),

                "reference": tags.get(
                    "ref"
                ),

                "technology": tags.get(
                    "telecom"
                ),

                "medium": tags.get(
                    "telecom:medium"
                ),

                "connection_type": tags.get(
                    "connection"
                ),

                "capacity": tags.get(
                    "capacity"
                ),

                "geometry": LineString(
                    coordinates
                ),
            }

            self.telecom_features.append(
                feature
            )

            count += 1

        print(
            f"Telecom Way Features : "
            f"{count}"
        )

    # =====================================================
    # POWER GEODATAFRAME
    # =====================================================

    def create_power_geodataframe(self):

        if not self.power_features:

            self.power_gdf = gpd.GeoDataFrame(
                {
                    "source": [],
                    "osm_id": [],
                    "element_type": [],
                    "power_type": [],
                    "name": [],
                    "operator": [],
                    "voltage": [],
                    "frequency": [],
                    "reference": [],
                },
                geometry=[],
                crs=self.CRS,
            )

        else:

            self.power_gdf = (
                gpd.GeoDataFrame(
                    self.power_features,
                    geometry="geometry",
                    crs=self.CRS,
                )
            )

        print("--------------------------------")

        print(
            f"Power GeoDataFrame Rows : "
            f"{len(self.power_gdf)}"
        )

        print(
            f"CRS                    : "
            f"{self.power_gdf.crs}"
        )

    # =====================================================
    # TELECOM GEODATAFRAME
    # =====================================================

    def create_telecom_geodataframe(self):

        if not self.telecom_features:

            self.telecom_gdf = gpd.GeoDataFrame(
                {
                    "source": [],
                    "osm_id": [],
                    "element_type": [],
                    "telecom_type": [],
                    "name": [],
                    "operator": [],
                    "reference": [],
                    "technology": [],
                    "medium": [],
                    "connection_type": [],
                    "capacity": [],
                },
                geometry=[],
                crs=self.CRS,
            )

        else:

            self.telecom_gdf = (
                gpd.GeoDataFrame(
                    self.telecom_features,
                    geometry="geometry",
                    crs=self.CRS,
                )
            )

        print("--------------------------------")

        print(
            f"Telecom GeoDataFrame Rows : "
            f"{len(self.telecom_gdf)}"
        )

        print(
            f"CRS                      : "
            f"{self.telecom_gdf.crs}"
        )

    # =====================================================
    # SAVE POWER GEOJSON
    # =====================================================

    def save_power_geojson(self):

        if self.power_gdf is None:

            raise RuntimeError(
                "Power GeoDataFrame "
                "has not been created."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        geojson = self.power_gdf.to_json(
            ensure_ascii=False,
        )

        self.power_output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")

        print(
            f"Saved Power : "
            f"{self.power_output_file}"
        )

    # =====================================================
    # SAVE TELECOM GEOJSON
    # =====================================================

    def save_telecom_geojson(self):

        if self.telecom_gdf is None:

            raise RuntimeError(
                "Telecom GeoDataFrame "
                "has not been created."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        geojson = self.telecom_gdf.to_json(
            ensure_ascii=False,
        )

        self.telecom_output_file.write_text(
            geojson,
            encoding="utf-8",
        )

        print("--------------------------------")

        print(
            f"Saved Telecom : "
            f"{self.telecom_output_file}"
        )