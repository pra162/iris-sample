"""
Energy Layer

Responsible for rendering Renewable Energy Assets
using PyDeck.
"""

import pydeck as pdk

from .map_styles import (
    ENERGY_COLOR,
    ENERGY_RADIUS,
)


def build_energy_layer(
    energy_assets: list[dict],
) -> pdk.Layer:
    """
    Returns the Renewable Energy layer.
    """

    if not energy_assets:
        return None

    return pdk.Layer(
        "ScatterplotLayer",

        data=energy_assets,

        get_position="[longitude, latitude]",

        get_fill_color=ENERGY_COLOR,

        get_radius=ENERGY_RADIUS,

        get_line_color=[255, 255, 255],

        line_width_min_pixels=2,

        stroked=True,
        filled=True,

        pickable=True,

        auto_highlight=True,

        radius_min_pixels=5,

        radius_max_pixels=18,

        opacity=0.9,
    )