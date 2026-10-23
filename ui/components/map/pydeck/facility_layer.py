"""
Facility Layer

Responsible for rendering Data Center facilities
using PyDeck.
"""

import pydeck as pdk

from .map_styles import (
    FACILITY_COLOR,
    FACILITY_RADIUS,
)


def build_facility_layer(
    facilities: list[dict],
) -> pdk.Layer:
    """
    Returns the Facility Scatterplot Layer.
    """

    if not facilities:
        return None

    data = []

    for facility in facilities:

        data.append(
                {
                    "id": str(facility["id"]),
                    "name": facility.get("name") or "Unknown Facility",
                    "company": facility.get("company") or "-",
                    "city": facility.get("city") or "-",
                    "country": facility.get("country") or "-",
                    "operator": facility.get("company") or "-",
                    "voltage": "-",
                    "latitude": facility.get("latitude"),
                    "longitude": facility.get("longitude"),
                }
            )

    return pdk.Layer(
        "ScatterplotLayer",

        id="facilities",

        data=data,

        get_position="[longitude, latitude]",

        get_radius=FACILITY_RADIUS,

        get_fill_color=FACILITY_COLOR,

        get_line_color=[255, 255, 255],

        stroked=True,
        filled=True,

        pickable=True,
        auto_highlight=True,

        line_width_min_pixels=3,

        highlight_color=[255, 215, 0, 220],

        # Increase these ↓↓↓
        radius_min_pixels=12,
        radius_max_pixels=40,
    )