"""
Energy Layer

Responsible for rendering Renewable Energy
Assets on the NRW Infrastructure Map.
"""

import folium

from .popup_builder import build_energy_popup

from .map_styles import (
    ENERGY_COLOR,
    ENERGY_BORDER,
    ENERGY_RADIUS,
    MARKER_BORDER_WEIGHT,
    MARKER_FILL_OPACITY,
)


# ==========================================================
# Public API
# ==========================================================

def add_energy_assets(
    m: folium.Map,
    energy_assets: list[dict],
) -> None:
    """
    Adds renewable energy assets
    to the map.
    """

    if not energy_assets:
        return

    layer = folium.FeatureGroup(
        name="☀ Renewable Energy",
        show=True,
    )

    for asset in energy_assets:

        latitude = asset.get("latitude")
        longitude = asset.get("longitude")

        if latitude is None or longitude is None:
            continue

        popup = folium.Popup(
            build_energy_popup(asset),
            max_width=300,
        )

        folium.CircleMarker(
            location=[
                latitude,
                longitude,
            ],
            radius=ENERGY_RADIUS,
            color=ENERGY_BORDER,
            weight=MARKER_BORDER_WEIGHT,
            fill=True,
            fill_color=ENERGY_COLOR,
            fill_opacity=MARKER_FILL_OPACITY,
            popup=popup,
            tooltip=asset.get("name") or "Energy Asset",
        ).add_to(layer)

    layer.add_to(m)