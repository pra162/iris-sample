"""
Transformer Layer

Responsible for rendering strategic
Transformers using PyDeck.
"""

import pydeck as pdk

from .map_styles import (
    TRANSFORMER_COLOR,
    TRANSFORMER_RADIUS,
)


def build_transformer_layer(
    transformers: list[dict],
) -> pdk.Layer:
    """
    Returns the Transformer layer.
    """

    if not transformers:
        return None

    return pdk.Layer(
        "ScatterplotLayer",

        data=transformers,

        get_position="[longitude, latitude]",

        get_fill_color=TRANSFORMER_COLOR,

        get_radius=TRANSFORMER_RADIUS,

        get_line_color=[255, 255, 255],

        line_width_min_pixels=2,

        stroked=True,
        filled=True,

        pickable=True,

        auto_highlight=True,

        radius_min_pixels=5,

        radius_max_pixels=18,
    )