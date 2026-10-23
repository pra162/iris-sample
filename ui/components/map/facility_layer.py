"""
Facility Layer

Responsible for rendering Data Center facilities
on the NRW Infrastructure Map.
"""

import folium

from .popup_builder import build_facility_popup

from .map_styles import (
    FACILITY_COLOR,
    FACILITY_BORDER,
    FACILITY_RADIUS,
    MARKER_BORDER_WEIGHT,
    MARKER_FILL_OPACITY,
)


# ==========================================================
# Public API
# ==========================================================

def add_facilities(
    m: folium.Map,
    facilities: list[dict],
) -> None:
    """
    Adds all facilities to the map.
    """

    if not facilities:
        return

    layer = folium.FeatureGroup(
        name="🏢 Data Centers",
        show=True,
    )

    for facility in facilities:

        latitude = facility.get("latitude")
        longitude = facility.get("longitude")

        if latitude is None or longitude is None:
            continue

        popup = folium.Popup(
            build_facility_popup(facility),
            max_width=300,
        )

        folium.CircleMarker(
            location=[
                latitude,
                longitude,
            ],
            radius=FACILITY_RADIUS,
            color=FACILITY_BORDER,
            weight=MARKER_BORDER_WEIGHT,
            fill=True,
            fill_color=FACILITY_COLOR,
            fill_opacity=MARKER_FILL_OPACITY,
            popup=popup,
            tooltip=facility.get("name") or "Facility",
        ).add_to(layer)

    layer.add_to(m)