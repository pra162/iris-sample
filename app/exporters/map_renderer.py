from __future__ import annotations

import json
import math
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from shapely import wkb
from shapely.ops import unary_union
from shapely.geometry import Point
from shapely.geometry import shape as shapely_shape
from sqlalchemy.orm import Session

from app.database.models.facility import Facility

from app.database.repositories.facility_repository import (
    FacilityRepository,
)

from app.database.repositories.power_infrastructure_repository import (
    PowerInfrastructureRepository,
)

from app.database.repositories.osm_infrastructure_repository import (
    OsmInfrastructureRepository,
)


class MapRenderer:
    """
    Generates a static IRIS Site Intelligence map.

    Data sources:

        iris_core.facilities
        iris_core.power_infrastructure
        iris_core.osm_infrastructure

    Map layers:

        - CartoDB Positron basemap
        - 10 km analysis boundary
        - Selected facility
        - Nearby facilities
        - 380 kV transmission lines
        - 220 kV transmission lines
        - 110 kV transmission lines
        - High-voltage substations
        - Strategic transformers
        - Internet / telecom network lines
        - Telecom connection points
        - Telecom towers
        - Nearest infrastructure highlights

    Output:

        data/exports/maps/<facility_id>.png

    Input spatial data:

        EPSG:4326

    Rendering CRS:

        EPSG:3857
    """

    DEFAULT_RADIUS_KM = 10

    OUTPUT_DIRECTORY = (
        Path("data")
        / "exports"
        / "maps"
    )

    MAX_SUBSTATION_LABELS = 4
    MAX_TRANSFORMER_LABELS = 3
    MAX_NEARBY_FACILITY_LABELS = 4

    # ======================================================
    # INIT
    # ======================================================

    def __init__(
        self,
        session: Session,
        output_directory: Path | None = None,
    ):
        self.session = session

        self.output_directory = (
            output_directory
            or self.OUTPUT_DIRECTORY
        )

        self.facility_repository = (
            FacilityRepository(session)
        )

        self.power_repository = (
            PowerInfrastructureRepository(session)
        )

        self.osm_repository = (
            OsmInfrastructureRepository(session)
        )

    # ======================================================
    # PUBLIC
    # ======================================================

    def render_facility(
        self,
        facility_id: str,
        radius_km: float = DEFAULT_RADIUS_KM,
    ) -> Path:

        print("--------------------------------")
        print("Generating IRIS site map")
        print("--------------------------------")

        facility = self._get_facility(
            facility_id
        )

        if facility is None:
            raise ValueError(
                f"Facility not found: {facility_id}"
            )

        if (
            facility.latitude is None
            or facility.longitude is None
        ):
            raise ValueError(
                "Facility does not have valid "
                "latitude/longitude coordinates."
            )

        print(
            f"Facility : {facility.name}"
        )

        print(
            f"Company  : {facility.company}"
        )

        print(
            f"City     : {facility.city}"
        )

        print(
            f"Latitude : {facility.latitude}"
        )

        print(
            f"Longitude: {facility.longitude}"
        )

        print(
            f"Radius   : {radius_km} km"
        )

        # ==================================================
        # Nearby facilities
        # ==================================================

        nearby_facilities = (
            self._get_nearby_facilities(
                facility,
                radius_km,
            )
        )

        # ==================================================
        # Power infrastructure
        # ==================================================

        print()
        print(
            "Loading power infrastructure..."
        )

        substations = (
            self.power_repository
            .get_high_voltage_substations()
        )

        lines = (
            self.power_repository
            .get_high_voltage_lines()
        )

        transformers = (
            self.power_repository
            .get_strategic_transformers()
        )

        # ==================================================
        # Filter by radius
        # ==================================================

        substations = (
            self._filter_power_rows(
                substations,
                facility,
                radius_km,
            )
        )

        lines = (
            self._filter_power_rows(
                lines,
                facility,
                radius_km,
            )
        )

        transformers = (
            self._filter_power_rows(
                transformers,
                facility,
                radius_km,
            )
        )

        # ==================================================
        # Internet / telecom infrastructure
        # ==================================================

        print()
        print("Loading internet / telecom infrastructure...")

        telecom_gdf = self._load_telecom_network(
            facility=facility,
            radius_km=radius_km,
        )

        telecom_line_count = 0
        telecom_point_count = 0

        if not telecom_gdf.empty:
            telecom_line_count = int(
                telecom_gdf.geometry.geom_type.isin(
                    ["LineString", "MultiLineString"]
                ).sum()
            )
            telecom_point_count = int(
                telecom_gdf.geometry.geom_type.isin(
                    ["Point", "MultiPoint"]
                ).sum()
            )

        # ==================================================
        # Statistics
        # ==================================================

        voltage_counts = (
            self._count_voltage_levels(lines)
        )

        print(
            f"Nearby facilities : "
            f"{len(nearby_facilities)}"
        )

        print(
            f"HV lines          : "
            f"{len(lines)}"
        )

        print(
            f"Substations       : "
            f"{len(substations)}"
        )

        print(
            f"Transformers      : "
            f"{len(transformers)}"
        )

        print(
            f"Internet lines    : "
            f"{telecom_line_count}"
        )

        print(
            f"Internet points   : "
            f"{telecom_point_count}"
        )

        print(
            f"110 kV lines      : "
            f"{voltage_counts['110']}"
        )

        print(
            f"220 kV lines      : "
            f"{voltage_counts['220']}"
        )

        print(
            f"380 kV lines      : "
            f"{voltage_counts['380']}"
        )

        # ==================================================
        # Nearest infrastructure
        # ==================================================

        nearest_line = self._nearest_row(
            lines
        )

        nearest_substation = self._nearest_row(
            substations
        )

        nearest_transformer = self._nearest_row(
            transformers
        )

        # ==================================================
        # Output
        # ==================================================

        output_file = (
            self.output_directory
            / f"{facility.id}.png"
        )

        self._render(
            facility=facility,
            nearby_facilities=nearby_facilities,
            lines=lines,
            substations=substations,
            transformers=transformers,
            telecom_gdf=telecom_gdf,
            nearest_line=nearest_line,
            nearest_substation=nearest_substation,
            nearest_transformer=nearest_transformer,
            output_file=output_file,
            radius_km=radius_km,
        )

        print("--------------------------------")
        print(
            "Map generated successfully:"
        )
        print(output_file)
        print("--------------------------------")

        return output_file

    # ======================================================
    # FACILITY
    # ======================================================

    def _get_facility(
        self,
        facility_id: str,
    ) -> Facility | None:

        return self.session.get(
            Facility,
            facility_id,
        )

    # ======================================================
    # NEARBY FACILITIES
    # ======================================================

    def _get_nearby_facilities(
        self,
        facility: Facility,
        radius_km: float,
    ) -> list[Facility]:

        return self.facility_repository.find_nearby(
            latitude=facility.latitude,
            longitude=facility.longitude,
            radius_km=radius_km,
        )

    # ======================================================
    # POWER FILTER
    # ======================================================

    def _filter_power_rows(
        self,
        rows: list[dict],
        facility: Facility,
        radius_km: float,
    ) -> list[dict]:
        """
        Filter infrastructure by distance from facility.

        The repository currently returns GeoJSON geometry
        strings. We convert those to Shapely and perform
        the distance calculation in EPSG:25832.
        """

        if not rows:
            return []

        site_point = Point(
            facility.longitude,
            facility.latitude,
        )

        site_gdf = gpd.GeoDataFrame(
            {
                "geometry": [
                    site_point
                ]
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        site_gdf = site_gdf.to_crs(
            "EPSG:25832"
        )

        site_geometry = (
            site_gdf.geometry.iloc[0]
        )

        radius_meters = (
            radius_km * 1000
        )

        result = []

        for row in rows:

            geometry_value = row.get(
                "geometry"
            )

            if not geometry_value:
                continue

            try:

                if isinstance(
                    geometry_value,
                    str,
                ):
                    geometry = shapely_shape(
                        json.loads(
                            geometry_value
                        )
                    )

                elif hasattr(
                    geometry_value,
                    "geom_type",
                ):
                    geometry = geometry_value

                else:
                    continue

                if geometry is None:
                    continue

                if geometry.is_empty:
                    continue

                geometry_gdf = (
                    gpd.GeoDataFrame(
                        {
                            "geometry": [
                                geometry
                            ]
                        },
                        geometry="geometry",
                        crs="EPSG:4326",
                    )
                )

                geometry_gdf = (
                    geometry_gdf.to_crs(
                        "EPSG:25832"
                    )
                )

                geometry_metric = (
                    geometry_gdf
                    .geometry
                    .iloc[0]
                )

                distance = (
                    site_geometry.distance(
                        geometry_metric
                    )
                )

                if distance <= radius_meters:

                    row_copy = dict(row)

                    row_copy[
                        "distance_km"
                    ] = round(
                        distance / 1000,
                        2,
                    )

                    result.append(
                        row_copy
                    )

            except Exception as exc:

                print(
                    "Warning: unable to process "
                    "power geometry:"
                )

                print(
                    f"    {exc}"
                )

        return result

    # ======================================================
    # VOLTAGE
    # ======================================================

    @staticmethod
    def _voltage_level(
        voltage,
    ) -> str:
        """
        Determine the highest strategic voltage.

        Examples:

            110000
                -> 110

            220000
                -> 220

            380000
                -> 380

            380000;220000;110000
                -> 380
        """

        if voltage is None:
            return "110"

        value = str(
            voltage
        )

        if "380000" in value:
            return "380"

        if "220000" in value:
            return "220"

        if "110000" in value:
            return "110"

        return "110"

    # ======================================================
    # VOLTAGE COUNTS
    # ======================================================

    @classmethod
    def _count_voltage_levels(
        cls,
        lines: list[dict],
    ) -> dict:

        result = {
            "110": 0,
            "220": 0,
            "380": 0,
        }

        for line in lines:

            level = cls._voltage_level(
                line.get("voltage")
            )

            if level in result:
                result[level] += 1

        return result

    # ======================================================
    # NEAREST ROW
    # ======================================================

    @staticmethod
    def _nearest_row(
        rows: list[dict],
    ) -> dict | None:

        if not rows:
            return None

        valid = [
            row
            for row in rows
            if row.get("distance_km")
            is not None
        ]

        if not valid:
            return None

        return min(
            valid,
            key=lambda row:
                row.get(
                    "distance_km",
                    math.inf,
                ),
        )

    # ======================================================
    # RENDER
    # ======================================================

    def _render(
        self,
        facility: Facility,
        nearby_facilities: list[Facility],
        lines: list[dict],
        substations: list[dict],
        transformers: list[dict],
        telecom_gdf: gpd.GeoDataFrame,
        nearest_line: dict | None,
        nearest_substation: dict | None,
        nearest_transformer: dict | None,
        output_file: Path,
        radius_km: float,
    ) -> None:

        # ==================================================
        # SELECTED FACILITY
        # ==================================================

        facility_geometry = (
            self._facility_geometry(
                facility
            )
        )

        facility_gdf = gpd.GeoDataFrame(
            {
                "name": [
                    facility.name
                ],
                "geometry": [
                    facility_geometry
                ],
            },
            geometry="geometry",
            crs="EPSG:4326",
        )

        # ==================================================
        # NEARBY FACILITIES
        # ==================================================

        nearby_rows = []

        for item in nearby_facilities:

            if item.id == facility.id:
                continue

            if item.geometry is None:
                continue

            try:

                geometry = (
                    self._facility_geometry(
                        item
                    )
                )

                nearby_rows.append(
                    {
                        "name": item.name,
                        "company": item.company,
                        "geometry": geometry,
                    }
                )

            except Exception:
                continue

        if nearby_rows:

            nearby_gdf = gpd.GeoDataFrame(
                nearby_rows,
                geometry="geometry",
                crs="EPSG:4326",
            )

        else:

            nearby_gdf = gpd.GeoDataFrame(
                {
                    "name": [],
                    "company": [],
                    "geometry": [],
                },
                geometry="geometry",
                crs="EPSG:4326",
            )

        # ==================================================
        # POWER GEODATAFRAMES
        # ==================================================

        lines_gdf = (
            self._power_geodataframe(
                lines
            )
        )

        substations_gdf = (
            self._power_geodataframe(
                substations
            )
        )

        transformers_gdf = (
            self._power_geodataframe(
                transformers
            )
        )

        # ==================================================
        # VOLTAGE LEVEL
        # ==================================================

        if not lines_gdf.empty:

            lines_gdf[
                "voltage_level"
            ] = (
                lines_gdf["voltage"]
                .apply(
                    self._voltage_level
                )
            )

        # ==================================================
        # REPROJECT
        # ==================================================

        facility_gdf = (
            facility_gdf.to_crs(
                "EPSG:3857"
            )
        )

        if not nearby_gdf.empty:

            nearby_gdf = (
                nearby_gdf.to_crs(
                    "EPSG:3857"
                )
            )

        if not lines_gdf.empty:

            lines_gdf = (
                lines_gdf.to_crs(
                    "EPSG:3857"
                )
            )

        if not substations_gdf.empty:

            substations_gdf = (
                substations_gdf.to_crs(
                    "EPSG:3857"
                )
            )

        if not transformers_gdf.empty:

            transformers_gdf = (
                transformers_gdf.to_crs(
                    "EPSG:3857"
                )
            )

        if not telecom_gdf.empty:
            telecom_gdf = telecom_gdf.to_crs(
                "EPSG:3857"
            )

        # ==================================================
        # FIGURE
        # ==================================================

        fig = plt.figure(
            figsize=(20, 12),
            facecolor="white",
        )

        ax = fig.add_axes(
            [
                0.035,
                0.065,
                0.745,
                0.825,
            ]
        )

        # ==================================================
        # SITE POINT
        # ==================================================

        selected_point = (
            facility_gdf.geometry.iloc[0]
        )

        x = selected_point.x
        y = selected_point.y

        # ==================================================
        # MAP EXTENT
        # ==================================================

        padding = (
            radius_km * 1000
        )

        ax.set_xlim(
            x - padding,
            x + padding,
        )

        ax.set_ylim(
            y - padding,
            y + padding,
        )

        # ==================================================
        # BASEMAP
        # ==================================================

        try:

            print(
                "Loading CartoDB basemap..."
            )

            ctx.add_basemap(
                ax,
                source=(
                    ctx.providers
                    .CartoDB
                    .Positron
                ),
                zoom="auto",
                attribution=True,
            )

        except Exception as exc:

            print(
                "Warning: CartoDB basemap "
                "could not be loaded."
            )

            print(
                f"    {exc}"
            )

        # ==================================================
        # ANALYSIS RADIUS
        # ==================================================

        radius_circle = Circle(
            (
                x,
                y,
            ),
            radius_km * 1000,
            facecolor="#2563EB",
            edgecolor="#1D4ED8",
            linewidth=2.0,
            linestyle="--",
            alpha=0.06,
            zorder=2,
        )

        ax.add_patch(
            radius_circle
        )

        # Boundary only

        boundary_circle = Circle(
            (
                x,
                y,
            ),
            radius_km * 1000,
            fill=False,
            edgecolor="#2563EB",
            linewidth=1.5,
            linestyle="--",
            alpha=0.65,
            zorder=3,
        )

        ax.add_patch(
            boundary_circle
        )

        # ==================================================
        # TRANSMISSION NETWORK
        # ==================================================

        self._plot_transmission_lines(
            ax,
            lines_gdf,
        )

        # ==================================================
        # INTERNET / TELECOM NETWORK
        # ==================================================
        # Render this layer early so the telecom network is visible
        # above the basemap but remains below the final site markers.

        self._plot_telecom_network(
            ax,
            telecom_gdf,
        )

        # ==================================================
        # NEAREST HV LINE HIGHLIGHT
        # ==================================================

        if (
            nearest_line
            and not lines_gdf.empty
        ):

            self._plot_nearest_line(
                ax,
                lines_gdf,
                nearest_line,
            )

        # ==================================================
        # NEARBY FACILITIES
        # ==================================================

        if not nearby_gdf.empty:

            nearby_gdf.plot(
                ax=ax,
                markersize=35,
                marker="o",
                color="#64748B",
                edgecolor="white",
                linewidth=0.8,
                alpha=0.80,
                zorder=8,
            )

        # ==================================================
        # SUBSTATIONS
        # ==================================================

        if not substations_gdf.empty:

            substations_gdf.plot(
                ax=ax,
                markersize=125,
                marker="^",
                color="#2563EB",
                edgecolor="white",
                linewidth=1.2,
                alpha=0.95,
                zorder=11,
            )

        # ==================================================
        # NEAREST SUBSTATION
        # ==================================================

        if (
            nearest_substation
            and not substations_gdf.empty
        ):

            self._plot_nearest_point(
                ax,
                substations_gdf,
                nearest_substation,
                marker="^",
                color="#0F172A",
                size=280,
                zorder=14,
            )

        # ==================================================
        # TRANSFORMERS
        # ==================================================

        if not transformers_gdf.empty:

            transformers_gdf.plot(
                ax=ax,
                markersize=70,
                marker="s",
                color="#7C3AED",
                edgecolor="white",
                linewidth=0.9,
                alpha=0.90,
                zorder=12,
            )

        # ==================================================
        # NEAREST TRANSFORMER
        # ==================================================

        if (
            nearest_transformer
            and not transformers_gdf.empty
        ):

            self._plot_nearest_point(
                ax,
                transformers_gdf,
                nearest_transformer,
                marker="s",
                color="#111827",
                size=190,
                zorder=14,
            )

        # ==================================================
        # SELECTED FACILITY
        # ==================================================

        facility_gdf.plot(
            ax=ax,
            markersize=520,
            marker="*",
            color="#111827",
            edgecolor="white",
            linewidth=2.0,
            zorder=20,
        )

        # ==================================================
        # SITE LABEL
        # ==================================================

        ax.annotate(
            facility.name,
            xy=(
                x,
                y,
            ),
            xytext=(
                15,
                15,
            ),
            textcoords="offset points",
            fontsize=11,
            fontweight="bold",
            color="#0F172A",
            bbox={
                "boxstyle":
                    "round,pad=0.45",
                "facecolor":
                    "white",
                "edgecolor":
                    "#111827",
                "linewidth":
                    1.2,
                "alpha":
                    0.96,
            },
            zorder=30,
        )

        # ==================================================
        # RADIUS LABEL
        # ==================================================

        ax.annotate(
            f"{radius_km:g} km analysis area",
            xy=(
                x + padding * 0.72,
                y,
            ),
            fontsize=9,
            color="#1D4ED8",
            fontweight="bold",
            bbox={
                "boxstyle":
                    "round,pad=0.3",
                "facecolor":
                    "white",
                "edgecolor":
                    "#93C5FD",
                "alpha":
                    0.90,
            },
            zorder=25,
        )

        # ==================================================
        # SUBSTATION LABELS
        # ==================================================

        self._add_substation_labels(
            ax,
            substations_gdf,
            nearest_substation,
        )

        # ==================================================
        # TRANSFORMER LABELS
        # ==================================================

        self._add_transformer_labels(
            ax,
            transformers_gdf,
            nearest_transformer,
        )

        # ==================================================
        # NEAREST HV LINE LABEL
        # ==================================================

        self._add_nearest_line_label(
            ax,
            lines_gdf,
            nearest_line,
        )

        # ==================================================
        # TITLE
        # ==================================================

        city = (
            facility.city
            or ""
        )

        fig.suptitle(
            "IRIS SITE INTELLIGENCE",
            x=0.04,
            y=0.965,
            ha="left",
            fontsize=22,
            fontweight="bold",
            color="#0F172A",
        )

        ax.set_title(
            (
                f"{facility.name}"
                f"  •  {city}"
            ),
            loc="left",
            fontsize=12,
            color="#64748B",
            pad=12,
        )

        # ==================================================
        # RIGHT INFORMATION PANEL
        # ==================================================

        self._draw_intelligence_panel(
            fig=fig,
            facility=facility,
            radius_km=radius_km,
            lines=lines,
            substations=substations,
            transformers=transformers,
            telecom_gdf=telecom_gdf,
            voltage_counts=(
                self._count_voltage_levels(
                    lines
                )
            ),
            nearest_line=nearest_line,
            nearest_substation=(
                nearest_substation
            ),
            nearest_transformer=(
                nearest_transformer
            ),
        )

        # ==================================================
        # LEGEND
        # ==================================================

        self._draw_legend(
            fig
        )

        # ==================================================
        # AXIS
        # ==================================================

        ax.set_axis_off()

        # ==================================================
        # SAVE
        # ==================================================

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fig.savefig(
            output_file,
            dpi=240,
            bbox_inches=None,
            facecolor="white",
        )

        plt.close(
            fig
        )

    # ======================================================
    # TRANSMISSION LINE RENDERING
    # ======================================================

    @staticmethod
    def _plot_transmission_lines(
        ax,
        lines_gdf: gpd.GeoDataFrame,
    ) -> None:
        """
        Draw the HV network as continuous transmission corridors.

        Overpass/OSM frequently stores one power corridor as many short
        LineString ways. Drawing each way independently makes the network
        look like disconnected dashes. We dissolve the visible segments by
        voltage level before rendering them.
        """

        if lines_gdf.empty:
            return

        styles = {
            "110": {
                "color": "#D97706",
                "glow": "#F59E0B",
                "width": 1.15,
                "glow_width": 3.8,
                "zorder": 5,
            },
            "220": {
                "color": "#C2410C",
                "glow": "#FB923C",
                "width": 2.15,
                "glow_width": 5.2,
                "zorder": 6,
            },
            "380": {
                "color": "#991B1B",
                "glow": "#DC2626",
                "width": 3.25,
                "glow_width": 7.0,
                "zorder": 7,
            },
        }

        for level, style in styles.items():
            layer = lines_gdf[
                lines_gdf["voltage_level"] == level
            ]

            if layer.empty:
                continue

            geometries = [
                geom
                for geom in layer.geometry
                if geom is not None and not geom.is_empty
            ]

            if not geometries:
                continue

            try:
                merged_geometry = unary_union(geometries)
            except Exception:
                merged_geometry = geometries

            merged = gpd.GeoSeries(
                [merged_geometry],
                crs=layer.crs,
            )

            # Soft glow/casing.
            merged.plot(
                ax=ax,
                linewidth=style["glow_width"],
                color=style["glow"],
                alpha=0.18,
                zorder=style["zorder"],
            )

            # Main voltage corridor.
            merged.plot(
                ax=ax,
                linewidth=style["width"],
                color=style["color"],
                alpha=0.96,
                zorder=style["zorder"] + 1,
            )

    @staticmethod
    def _plot_nearest_line(
        ax,
        lines_gdf: gpd.GeoDataFrame,
        nearest_line: dict,
    ) -> None:
        """Highlight the exact nearest HV line segment."""

        if not nearest_line or lines_gdf.empty:
            return

        row_id = nearest_line.get("id")
        target_name = nearest_line.get("name")
        target_level = MapRenderer._voltage_level(
            nearest_line.get("voltage")
        )

        candidates = lines_gdf[
            lines_gdf["voltage_level"] == target_level
        ].copy()

        if row_id is not None and "id" in candidates.columns:
            exact = candidates[candidates["id"] == row_id]
            if not exact.empty:
                candidates = exact

        if (
            len(candidates) > 1
            and target_name
            and "name" in candidates.columns
        ):
            named = candidates[
                candidates["name"]
                .fillna("")
                .astype(str)
                .str.strip()
                == str(target_name).strip()
            ]
            if not named.empty:
                candidates = named

        if candidates.empty:
            return

        if "distance_km" in candidates.columns:
            candidates = candidates.sort_values(
                "distance_km"
            ).head(1)

        # White casing makes the selected corridor visible over all
        # voltage layers and the basemap.
        candidates.plot(
            ax=ax,
            linewidth=7.0,
            color="white",
            alpha=0.95,
            zorder=18,
        )

        candidates.plot(
            ax=ax,
            linewidth=3.5,
            color="#2563EB",
            alpha=1.0,
            zorder=19,
        )

    @staticmethod
    def _plot_nearest_point(
        ax,
        gdf: gpd.GeoDataFrame,
        row: dict,
        marker: str,
        color: str,
        size: float,
        zorder: int,
    ) -> None:

        distance = row.get(
            "distance_km"
        )

        if distance is None:
            return

        row_id = row.get(
            "id"
        )

        candidates = gdf

        if row_id is not None:
            candidates = gdf[
                gdf["id"] == row_id
            ]

        if candidates.empty:
            return

        candidates.plot(
            ax=ax,
            markersize=size,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=1.5,
            zorder=zorder,
        )

    # ======================================================
    # SUBSTATION LABELS
    # ======================================================

    @staticmethod
    def _add_substation_labels(
        ax,
        substations_gdf: gpd.GeoDataFrame,
        nearest_substation: dict | None,
    ) -> None:

        if substations_gdf.empty:
            return

        if "name" not in substations_gdf.columns:
            return

        named = substations_gdf[
            substations_gdf["name"]
            .notna()
            & (
                substations_gdf["name"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

        if named.empty:
            return

        if "distance_km" in named.columns:

            named = (
                named
                .sort_values(
                    "distance_km"
                )
                .head(
                    MapRenderer
                    .MAX_SUBSTATION_LABELS
                )
            )

        else:

            named = named.head(
                MapRenderer
                .MAX_SUBSTATION_LABELS
            )

        for _, row in named.iterrows():

            geometry = row.geometry

            if geometry is None:
                continue

            if geometry.geom_type in (
                "Polygon",
                "MultiPolygon",
                "LineString",
                "MultiLineString",
            ):
                point = (
                    geometry.centroid
                )
            else:
                point = geometry

            name = str(
                row["name"]
            )

            distance = row.get(
                "distance_km"
            )

            if distance is not None:

                label = (
                    f"{name}\n"
                    f"{distance:.2f} km"
                )

            else:

                label = name

            ax.annotate(
                label,
                xy=(
                    point.x,
                    point.y,
                ),
                xytext=(
                    8,
                    8,
                ),
                textcoords="offset points",
                fontsize=8.5,
                fontweight="bold",
                color="#1E3A8A",
                bbox={
                    "boxstyle":
                        "round,pad=0.28",
                    "facecolor":
                        "white",
                    "edgecolor":
                        "#60A5FA",
                    "alpha":
                        0.92,
                },
                zorder=25,
            )

    # ======================================================
    # TRANSFORMER LABELS
    # ======================================================

    @staticmethod
    def _add_transformer_labels(
        ax,
        transformers_gdf: gpd.GeoDataFrame,
        nearest_transformer: dict | None,
    ) -> None:

        if transformers_gdf.empty:
            return

        if "name" not in transformers_gdf.columns:
            return

        named = transformers_gdf[
            transformers_gdf["name"]
            .notna()
            & (
                transformers_gdf["name"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

        if named.empty:
            return

        if "distance_km" in named.columns:

            named = (
                named
                .sort_values(
                    "distance_km"
                )
                .head(
                    MapRenderer
                    .MAX_TRANSFORMER_LABELS
                )
            )

        else:

            named = named.head(
                MapRenderer
                .MAX_TRANSFORMER_LABELS
            )

        for _, row in named.iterrows():

            geometry = row.geometry

            if geometry is None:
                continue

            if geometry.geom_type in (
                "Polygon",
                "MultiPolygon",
                "LineString",
                "MultiLineString",
            ):
                point = (
                    geometry.centroid
                )
            else:
                point = geometry

            name = str(
                row["name"]
            )

            distance = row.get(
                "distance_km"
            )

            if distance is not None:

                label = (
                    f"{name}\n"
                    f"{distance:.2f} km"
                )

            else:

                label = name

            ax.annotate(
                label,
                xy=(
                    point.x,
                    point.y,
                ),
                xytext=(
                    8,
                    -18,
                ),
                textcoords="offset points",
                fontsize=8.5,
                color="#6B21A8",
                bbox={
                    "boxstyle":
                        "round,pad=0.28",
                    "facecolor":
                        "white",
                    "edgecolor":
                        "#C084FC",
                    "alpha":
                        0.92,
                },
                zorder=25,
            )

    # ======================================================
    # NEAREST LINE LABEL
    # ======================================================

    @staticmethod
    def _add_nearest_line_label(
        ax,
        lines_gdf: gpd.GeoDataFrame,
        nearest_line: dict | None,
    ) -> None:

        if nearest_line is None:
            return

        if lines_gdf.empty:
            return

        target_level = (
            MapRenderer._voltage_level(
                nearest_line.get(
                    "voltage"
                )
            )
        )

        candidates = lines_gdf[
            lines_gdf[
                "voltage_level"
            ] == target_level
        ]

        if candidates.empty:
            return

        candidates = candidates.copy()

        if "distance_km" in candidates.columns:

            candidates = (
                candidates
                .sort_values(
                    "distance_km"
                )
                .head(1)
            )

        row = candidates.iloc[0]

        geometry = row.geometry

        if geometry is None:
            return

        point = (
            geometry.interpolate(
                0.5,
                normalized=True,
            )
            if geometry.geom_type
            in (
                "LineString",
                "MultiLineString",
            )
            else geometry
        )

        distance = nearest_line.get(
            "distance_km"
        )

        voltage = (
            f"{target_level} kV"
        )

        label = (
            f"Nearest HV line\n"
            f"{voltage}"
        )

        if distance is not None:
            label += (
                f" • {distance:.2f} km"
            )

        ax.annotate(
            label,
            xy=(
                point.x,
                point.y,
            ),
            xytext=(
                10,
                -25,
            ),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            color="#1D4ED8",
            bbox={
                "boxstyle":
                    "round,pad=0.35",
                "facecolor":
                    "white",
                "edgecolor":
                    "#2563EB",
                "linewidth":
                    1.2,
                "alpha":
                    0.95,
            },
            zorder=28,
        )

    # ======================================================
    # INTELLIGENCE PANEL
    # ======================================================

    @staticmethod
    def _draw_intelligence_panel(
        fig,
        facility: Facility,
        radius_km: float,
        lines: list[dict],
        substations: list[dict],
        transformers: list[dict],
        telecom_gdf: gpd.GeoDataFrame,
        voltage_counts: dict,
        nearest_line: dict | None,
        nearest_substation: dict | None,
        nearest_transformer: dict | None,
    ) -> None:

        panel = fig.add_axes(
            [
                0.785,
                0.48,
                0.185,
                0.37,
            ]
        )

        panel.set_axis_off()

        panel.text(
            0.0,
            1.0,
            "SITE INTELLIGENCE",
            fontsize=14,
            fontweight="bold",
            color="#0F172A",
            va="top",
        )

        panel.text(
            0.0,
            0.91,
            facility.name or "Selected Site",
            fontsize=9,
            color="#475569",
            va="top",
            wrap=True,
        )

        panel.plot(
            [0, 1],
            [0.84, 0.84],
            transform=panel.transAxes,
            linewidth=1,
            color="#E2E8F0",
        )

        y = 0.77

        def add_metric(
            label: str,
            value: str,
            value_color="#0F172A",
        ):
            nonlocal y

            panel.text(
                0.0,
                y,
                label,
                fontsize=8.5,
                color="#64748B",
                va="top",
            )

            panel.text(
                1.0,
                y,
                value,
                fontsize=9.5,
                fontweight="bold",
                color=value_color,
                ha="right",
                va="top",
            )

            y -= 0.085

        add_metric(
            "Analysis radius",
            f"{radius_km:g} km",
        )

        add_metric(
            "HV line segments",
            f"{len(lines):,}",
        )

        add_metric(
            "Substations",
            f"{len(substations):,}",
        )

        add_metric(
            "Transformers",
            f"{len(transformers):,}",
        )

        telecom_lines = 0
        telecom_points = 0

        if not telecom_gdf.empty:
            telecom_lines = int(
                telecom_gdf.geometry.geom_type.isin(
                    ["LineString", "MultiLineString"]
                ).sum()
            )
            telecom_points = int(
                telecom_gdf.geometry.geom_type.isin(
                    ["Point", "MultiPoint"]
                ).sum()
            )

        add_metric(
            "Internet lines",
            f"{telecom_lines:,}",
            "#0891B2",
        )

        add_metric(
            "Internet points",
            f"{telecom_points:,}",
            "#0E7490",
        )

        y -= 0.025

        panel.text(
            0.0,
            y,
            "TRANSMISSION GRID",
            fontsize=8,
            fontweight="bold",
            color="#0F172A",
            va="top",
        )

        y -= 0.075

        add_metric(
            "380 kV",
            f"{voltage_counts['380']:,}",
            "#991B1B",
        )

        add_metric(
            "220 kV",
            f"{voltage_counts['220']:,}",
            "#C2410C",
        )

        add_metric(
            "110 kV",
            f"{voltage_counts['110']:,}",
            "#D97706",
        )

        y -= 0.02

        panel.text(
            0.0,
            y,
            "NEAREST INFRASTRUCTURE",
            fontsize=8,
            fontweight="bold",
            color="#0F172A",
            va="top",
        )

        y -= 0.075

        # --------------------------------------------------
        # HV line
        # --------------------------------------------------

        if nearest_line:

            level = (
                MapRenderer._voltage_level(
                    nearest_line.get(
                        "voltage"
                    )
                )
            )

            distance = (
                nearest_line.get(
                    "distance_km"
                )
            )

            value = (
                f"{distance:.2f} km"
                if distance is not None
                else "—"
            )

            add_metric(
                f"HV line ({level} kV)",
                value,
                "#2563EB",
            )

        else:

            add_metric(
                "HV line",
                "Not found",
                "#64748B",
            )

        # --------------------------------------------------
        # Substation
        # --------------------------------------------------

        if nearest_substation:

            distance = (
                nearest_substation.get(
                    "distance_km"
                )
            )

            value = (
                f"{distance:.2f} km"
                if distance is not None
                else "—"
            )

            add_metric(
                "Substation",
                value,
                "#1D4ED8",
            )

        else:

            add_metric(
                "Substation",
                "Not found",
                "#64748B",
            )

        # --------------------------------------------------
        # Transformer
        # --------------------------------------------------

        if nearest_transformer:

            distance = (
                nearest_transformer.get(
                    "distance_km"
                )
            )

            value = (
                f"{distance:.2f} km"
                if distance is not None
                else "—"
            )

            add_metric(
                "Transformer",
                value,
                "#7C3AED",
            )

        else:

            add_metric(
                "Transformer",
                "Not found",
                "#64748B",
            )

        # --------------------------------------------------
        # Panel border
        # --------------------------------------------------

        panel.patch.set_facecolor(
            "white"
        )

        panel.patch.set_alpha(
            0.96
        )

        panel.patch.set_edgecolor(
            "#CBD5E1"
        )

        panel.patch.set_linewidth(
            1.2
        )

    # ======================================================
    # LEGEND
    # ======================================================

    @staticmethod
    def _draw_legend(
        fig,
    ) -> None:

        legend_ax = fig.add_axes(
            [
                0.795,
                0.065,
                0.185,
                0.315,
            ]
        )

        legend_ax.set_axis_off()

        legend_ax.text(
            0.0,
            1.0,
            "MAP LEGEND",
            fontsize=14,
            fontweight="bold",
            color="#0F172A",
            va="top",
        )

        handles = [
            Line2D(
                [0],
                [0],
                marker="*",
                color="w",
                markerfacecolor="#111827",
                markeredgecolor="white",
                markersize=17,
                label="Selected site",
            ),
            Line2D(
                [0],
                [0],
                marker="^",
                color="w",
                markerfacecolor="#2563EB",
                markeredgecolor="white",
                markersize=12,
                label="HV substation",
            ),
            Line2D(
                [0],
                [0],
                marker="s",
                color="w",
                markerfacecolor="#7C3AED",
                markeredgecolor="white",
                markersize=11,
                label="Transformer",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#64748B",
                markeredgecolor="white",
                markersize=10,
                label="Nearby data center",
            ),
            Line2D(
                [0],
                [0],
                color="#991B1B",
                linewidth=4.5,
                label="380 kV transmission",
            ),
            Line2D(
                [0],
                [0],
                color="#C2410C",
                linewidth=3.2,
                label="220 kV transmission",
            ),
            Line2D(
                [0],
                [0],
                color="#D97706",
                linewidth=2.0,
                label="110 kV transmission",
            ),
            Line2D(
                [0],
                [0],
                color="#06B6D4",
                linewidth=4.0,
                linestyle=(0, (8, 4)),
                label="Internet / fiber network",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#0891B2",
                markeredgecolor="white",
                markersize=11,
                label="Telecom connection point",
            ),
            Line2D(
                [0],
                [0],
                marker="^",
                color="w",
                markerfacecolor="#0E7490",
                markeredgecolor="white",
                markersize=12,
                label="Telecom tower",
            ),
            Line2D(
                [0],
                [0],
                color="#2563EB",
                linewidth=2.7,
                linestyle="--",
                label="10 km analysis boundary",
            ),
        ]

        legend = legend_ax.legend(
            handles=handles,
            loc="upper left",
            bbox_to_anchor=(
                0,
                0.88,
            ),
            frameon=False,
            fontsize=11.5,
            handlelength=3.4,
            labelspacing=1.05,
        )

        for text in legend.get_texts():
            text.set_color(
                "#334155"
            )

    # ======================================================
    # TELECOM / INTERNET NETWORK
    # ======================================================

    def _load_telecom_network(
        self,
        facility: Facility,
        radius_km: float,
    ) -> gpd.GeoDataFrame:
        """
        Load OSM telecom infrastructure directly from PostGIS.

        The ETL already stores the normalized OSM infrastructure in
        iris_core.osm_infrastructure. The renderer therefore does not
        read the old processed GeoJSON file anymore.

        For the first version the telecom layer uses the same 10 km
        analysis radius as the rest of the map. The public radius
        parameter is kept so it can become configurable later.
        """

        telecom_types = {
            "telecom",
            "telecom_line",
            "communication_line",
            "fibre",
            "exchange",
            "connection_point",
            "telecom_utility",
            "communication_tower",
            "communications_tower",
            "communication_mast",
            "service_device",
            "data_center",
        }

        country_code = (
            getattr(facility, "country_code", None)
            or "DE"
        )

        print(
            f"Telecom radius : {radius_km:g} km"
        )
        print(
            "Loading telecom infrastructure from PostGIS..."
        )

        try:
            rows = self.osm_repository.find_nearby(
                latitude=float(facility.latitude),
                longitude=float(facility.longitude),
                radius_km=radius_km,
                country_code=country_code,
            )
            print(f"Total OSM infrastructure rows loaded: {len(rows)}")
            
            # Debug: show unique infrastructure types
            if rows:
                unique_types = set()
                for row in rows:
                    infra_type = row.get("infrastructure_type")
                    if infra_type:
                        unique_types.add(str(infra_type).lower())
                print(f"Unique infrastructure types in database: {sorted(unique_types)}")
        except Exception as exc:
            print(
                "Warning: unable to load OSM telecom data:"
            )
            print(f"    {exc}")
            return gpd.GeoDataFrame(
                {"geometry": []},
                geometry="geometry",
                crs="EPSG:4326",
            )

        geometries = []
        properties = []

        for row in rows:
            infrastructure_type = str(
                row.get("infrastructure_type") or ""
            ).strip().lower()

            if infrastructure_type not in telecom_types:
                continue

            geometry_value = row.get("geometry")

            if not geometry_value:
                continue

            try:
                if isinstance(geometry_value, str):
                    geometry = shapely_shape(
                        json.loads(geometry_value)
                    )
                elif hasattr(geometry_value, "geom_type"):
                    geometry = geometry_value
                else:
                    continue

                if geometry is None or geometry.is_empty:
                    continue

                item = dict(row)
                item["infrastructure_type"] = infrastructure_type
                item["telecom_category"] = self._telecom_category(
                    item,
                    geometry,
                )

                geometries.append(geometry)
                properties.append(item)

            except Exception as exc:
                print(
                    "Warning: unable to parse OSM telecom geometry:"
                )
                print(f"    {exc}")

        if not geometries:
            print("Nearby telecom features : 0")
            return gpd.GeoDataFrame(
                {"geometry": []},
                geometry="geometry",
                crs="EPSG:4326",
            )

        result = gpd.GeoDataFrame(
            properties,
            geometry=geometries,
            crs="EPSG:4326",
        )

        print(
            f"Nearby telecom features : {len(result)}"
        )
        print("Telecom geometry types:")

        for geometry_type, count in (
            result.geometry.geom_type.value_counts().items()
        ):
            print(f"    {geometry_type}: {count}")

        print("Telecom infrastructure types:")

        for infrastructure_type, count in (
            result["infrastructure_type"]
            .value_counts()
            .items()
        ):
            print(f"    {infrastructure_type}: {count}")

        return result

    @staticmethod
    def _telecom_category(
        row,
        geometry=None,
    ) -> str:
        """
        Classify telecom geometry.

        Geometry is deliberately checked first. A real LineString or
        MultiLineString is rendered as a network line even if its OSM
        infrastructure_type is 'exchange', 'telecom_utility', etc.
        """

        geometry_type = (
            geometry.geom_type
            if geometry is not None
            else ""
        )

        if geometry_type in (
            "LineString",
            "MultiLineString",
        ):
            return "line"

        values = []

        for field in (
            "infrastructure_type",
            "telecom_type",
            "telecom",
            "tower_type",
            "feature_type",
            "type",
            "category",
            "man_made",
        ):
            if field in row:
                value = row.get(field)
                if value is not None:
                    values.append(str(value).lower())

        combined = " ".join(values)

        if (
            "tower" in combined
            or "mast" in combined
            or "communication_tower" in combined
        ):
            return "tower"

        return "point"

    @staticmethod
    def _plot_telecom_network(
        ax,
        telecom_gdf: gpd.GeoDataFrame,
    ) -> None:
        """
        Render the actual telecom geometries from PostGIS.

        Lines are drawn as a solid cyan corridor with a white casing so
        they remain visible over the basemap. Points and towers retain
        the visual treatment from the existing IRIS map.
        """

        if telecom_gdf.empty:
            print(
                "Telecom layer : no nearby features to render"
            )
            return

        line_mask = telecom_gdf.geometry.geom_type.isin(
            ["LineString", "MultiLineString"]
        )
        line_gdf = telecom_gdf[line_mask]

        point_mask = telecom_gdf.geometry.geom_type.isin(
            ["Point", "MultiPoint"]
        )
        point_gdf = telecom_gdf[point_mask]

        if not line_gdf.empty:
            print(f"Rendering {len(line_gdf)} telecom lines with increased visibility...")
            
            # Debug: check line bounds
            bounds = line_gdf.total_bounds
            print(f"Telecom line bounds: {bounds}")
            print(f"Line geometries sample:")
            for idx, geom in enumerate(line_gdf.geometry.head(3)):
                print(f"  Line {idx}: {geom.geom_type}, length: {geom.length:.2f}m")
            
            # White casing first for contrast against the basemap.
            line_gdf.plot(
                ax=ax,
                linewidth=15.0,
                color="white",
                alpha=1.0,
                zorder=50,
            )

            # Solid cyan Internet/fiber network.
            line_gdf.plot(
                ax=ax,
                linewidth=8.0,
                color="#06B6D4",
                alpha=1.0,
                zorder=51,
            )
            
            # Add point markers at line endpoints to make short lines visible
            for geom in line_gdf.geometry:
                if geom.geom_type == "LineString":
                    # Get endpoints
                    coords = list(geom.coords)
                    if len(coords) >= 2:
                        start_point = Point(coords[0])
                        end_point = Point(coords[-1])
                        
                        # Plot endpoints as cyan dots
                        gpd.GeoDataFrame(
                            {"geometry": [start_point, end_point]},
                            geometry="geometry",
                            crs=line_gdf.crs
                        ).plot(
                            ax=ax,
                            markersize=40,
                            marker="o",
                            color="#06B6D4",
                            edgecolor="white",
                            linewidth=1.5,
                            zorder=52,
                        )
            
            print("Telecom lines plotted successfully with endpoint markers")

        if not point_gdf.empty:
            tower_mask = point_gdf.apply(
                MapRenderer._is_telecom_tower,
                axis=1,
            )

            other_gdf = point_gdf[~tower_mask]
            tower_gdf = point_gdf[tower_mask]

            if not other_gdf.empty:
                other_gdf.plot(
                    ax=ax,
                    markersize=110,
                    marker="o",
                    color="white",
                    alpha=1.0,
                    zorder=26,
                )
                other_gdf.plot(
                    ax=ax,
                    markersize=62,
                    marker="o",
                    color="#0891B2",
                    edgecolor="white",
                    linewidth=1.1,
                    alpha=1.0,
                    zorder=27,
                )

            if not tower_gdf.empty:
                tower_gdf.plot(
                    ax=ax,
                    markersize=145,
                    marker="^",
                    color="white",
                    alpha=1.0,
                    zorder=28,
                )
                tower_gdf.plot(
                    ax=ax,
                    markersize=88,
                    marker="^",
                    color="#0E7490",
                    edgecolor="white",
                    linewidth=1.1,
                    alpha=1.0,
                    zorder=29,
                )

        print(
            "Telecom rendered : "
            f"{len(line_gdf)} lines, "
            f"{len(point_gdf)} points"
        )

    @staticmethod
    def _is_telecom_tower(row) -> bool:
        category = row.get("telecom_category")

        if category:
            return str(category).lower() == "tower"

        values = []

        for field in (
            "infrastructure_type",
            "telecom_type",
            "telecom",
            "tower_type",
            "feature_type",
            "man_made",
            "type",
        ):
            if field in row.index:
                value = row.get(field)
                if value is not None:
                    values.append(str(value).lower())

        combined = " ".join(values)

        return (
            "tower" in combined
            or "mast" in combined
            or "communication_tower" in combined
        )

    # ======================================================
    # FACILITY GEOMETRY
    # ======================================================

    @staticmethod
    def _facility_geometry(
        facility: Facility,
    ):
        """
        Convert GeoAlchemy WKBElement
        into Shapely geometry.
        """

        geometry = (
            facility.geometry
        )

        if geometry is None:

            if (
                facility.latitude
                is not None
                and facility.longitude
                is not None
            ):
                return Point(
                    facility.longitude,
                    facility.latitude,
                )

            raise ValueError(
                f"Facility '{facility.name}' "
                "does not have geometry."
            )

        # --------------------------------------------------
        # GeoAlchemy WKBElement
        # --------------------------------------------------

        if hasattr(
            geometry,
            "data",
        ):

            return wkb.loads(
                bytes(
                    geometry.data
                )
            )

        # --------------------------------------------------
        # Raw WKB
        # --------------------------------------------------

        if isinstance(
            geometry,
            bytes,
        ):

            return wkb.loads(
                geometry
            )

        # --------------------------------------------------
        # Already Shapely
        # --------------------------------------------------

        if hasattr(
            geometry,
            "geom_type",
        ):

            return geometry

        raise TypeError(
            "Unsupported facility "
            "geometry type: "
            f"{type(geometry)}"
        )

    # ======================================================
    # POWER GEODATAFRAME
    # ======================================================

    @staticmethod
    def _power_geodataframe(
        rows: list[dict],
    ) -> gpd.GeoDataFrame:
        """
        Convert repository GeoJSON rows
        into a GeoDataFrame.
        """

        geometries = []
        properties = []

        for row in rows:

            geometry_value = (
                row.get(
                    "geometry"
                )
            )

            if not geometry_value:
                continue

            try:

                # ------------------------------------------
                # GeoJSON string
                # ------------------------------------------

                if isinstance(
                    geometry_value,
                    str,
                ):

                    geometry = (
                        shapely_shape(
                            json.loads(
                                geometry_value
                            )
                        )
                    )

                # ------------------------------------------
                # Already Shapely
                # ------------------------------------------

                elif hasattr(
                    geometry_value,
                    "geom_type",
                ):

                    geometry = (
                        geometry_value
                    )

                else:
                    continue

                if geometry is None:
                    continue

                if geometry.is_empty:
                    continue

                row_copy = dict(
                    row
                )

                row_copy.pop(
                    "geometry",
                    None,
                )

                geometries.append(
                    geometry
                )

                properties.append(
                    row_copy
                )

            except Exception as exc:

                print(
                    "Warning: unable to parse "
                    "power geometry:"
                )

                print(
                    f"    {exc}"
                )

        # --------------------------------------------------
        # Empty layer
        # --------------------------------------------------

        if not geometries:

            return gpd.GeoDataFrame(
                {
                    "geometry": [],
                },
                geometry="geometry",
                crs="EPSG:4326",
            )

        # --------------------------------------------------
        # Normal layer
        # --------------------------------------------------

        return gpd.GeoDataFrame(
            properties,
            geometry=geometries,
            crs="EPSG:4326",
        )