"""
Transformer Layer

Responsible for rendering strategic
transformers using PyDeck.
"""

import pydeck as pdk

from .map_styles import (
    TRANSFORMER_COLOR,
    TRANSFORMER_RADIUS,
)


def build_transformer_layer(
    transformers: list[dict],
) -> pdk.Layer | None:
    """
    Returns the Transformer Scatterplot Layer.
    """

    if not transformers:
        return None

    data = []

    for transformer in transformers:

        # Convert SQLAlchemy Row -> dict
        if hasattr(transformer, "_mapping"):
            transformer = dict(transformer._mapping)
        else:
            transformer = dict(transformer)

        latitude = transformer.get("latitude")
        longitude = transformer.get("longitude")

        # Skip invalid coordinates
        if latitude is None or longitude is None:
            continue

        data.append(
            {
                "id": str(transformer.get("id", "")),
                "name": transformer.get("name") or "Transformer",
                "company": transformer.get("company")
                    or transformer.get("operator")
                    or "-",
                "operator": transformer.get("operator") or "-",
                "city": transformer.get("city") or "-",
                "voltage": transformer.get("voltage") or "-",
                "latitude": float(latitude),
                "longitude": float(longitude),
            }
        )

    if not data:
        return None

    return pdk.Layer(
        "ScatterplotLayer",

        id="transformers",

        data=data,

        get_position="[longitude, latitude]",

        get_radius=TRANSFORMER_RADIUS,

        get_fill_color=TRANSFORMER_COLOR,

        get_line_color=[255, 255, 255],

        stroked=True,
        filled=True,

        line_width_min_pixels=2,

        pickable=True,
        auto_highlight=True,

        opacity=0.95,

        radius_min_pixels=6,
        radius_max_pixels=18,

        highlight_color=[255, 215, 0, 255],
    )