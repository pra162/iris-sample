"""
Substation Layer

Responsible for rendering High Voltage
Substations on the NRW map.
"""

import folium

from .popup_builder import build_substation_popup

from .map_styles import (
    SUBSTATION_110KV_COLOR,
    SUBSTATION_220KV_COLOR,
    SUBSTATION_380KV_COLOR,
    SUBSTATION_110KV_RADIUS,
    SUBSTATION_220KV_RADIUS,
    SUBSTATION_380KV_RADIUS,
    SUBSTATION_BORDER,
    MARKER_BORDER_WEIGHT,
    MARKER_FILL_OPACITY,
)


# ==========================================================
# Helpers
# ==========================================================

def _substation_style(voltage: str | None) -> tuple[str, int]:
    """
    Returns marker color and radius
    based on voltage level.
    """

    voltage = voltage or ""

    if "380000" in voltage:
        return (
            SUBSTATION_380KV_COLOR,
            SUBSTATION_380KV_RADIUS,
        )

    if "220000" in voltage:
        return (
            SUBSTATION_220KV_COLOR,
            SUBSTATION_220KV_RADIUS,
        )

    return (
        SUBSTATION_110KV_COLOR,
        SUBSTATION_110KV_RADIUS,
    )


# ==========================================================
# Public API
# ==========================================================

def add_substations(
    m: folium.Map,
    substations: list[dict],
) -> None:
    """
    Adds all strategic substations
    to the map.
    """

    if not substations:
        return

    layer = folium.FeatureGroup(
        name="🏭 HV Substations",
        show=True,
    )

    for station in substations:

        latitude = station.get("latitude")
        longitude = station.get("longitude")

        if latitude is None or longitude is None:
            continue

        color, radius = _substation_style(
            station.get("voltage")
        )

        popup = folium.Popup(
            build_substation_popup(station),
            max_width=280,
        )

        folium.CircleMarker(
            location=[
                latitude,
                longitude,
            ],
            radius=radius,
            color=SUBSTATION_BORDER,
            weight=MARKER_BORDER_WEIGHT,
            fill=True,
            fill_color=color,
            fill_opacity=MARKER_FILL_OPACITY,
            popup=popup,
            tooltip=station.get("name") or "Substation",
        ).add_to(layer)

    layer.add_to(m)