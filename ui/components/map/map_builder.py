"""
Map Builder

Responsible for creating the base Folium map.

No business logic.
No layers.
No markers.
"""

import folium

from folium.plugins import (
    Fullscreen,
    MiniMap,
    MousePosition,
)

from .map_styles import (
    MAP_CENTER,
    MAP_ZOOM,
    MAP_TILES,
)


def create_base_map() -> folium.Map:
    """
    Creates the professional NRW Infrastructure Map.
    """

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=MAP_TILES,
        control_scale=True,
        prefer_canvas=True,
        zoom_control=True,
        max_zoom=18,
        min_zoom=6,
    )

    # --------------------------------------------------
    # Fullscreen Button
    # --------------------------------------------------

    Fullscreen(
        position="topright",
        title="Expand",
        title_cancel="Exit",
        force_separate_button=True,
    ).add_to(m)

    # --------------------------------------------------
    # Mini Map
    # --------------------------------------------------

    MiniMap(
        position="bottomright",
        toggle_display=True,
    ).add_to(m)

    # --------------------------------------------------
    # Mouse Coordinates
    # --------------------------------------------------

    MousePosition(
        position="bottomleft",
        separator=" | ",
        prefix="Coordinates",
        num_digits=6,
    ).add_to(m)

    return m