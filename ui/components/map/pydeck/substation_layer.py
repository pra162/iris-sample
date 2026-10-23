"""
Substation Layer

Responsible for rendering High Voltage
Substations using PyDeck.
"""

import pydeck as pdk

from .map_styles import (
    SUBSTATION_110KV,
    SUBSTATION_220KV,
    SUBSTATION_380KV,
    SUBSTATION_RADIUS,
)


# def _get_color(voltage: str | None) -> list[int]:
#     """
#     Returns RGB color based on voltage.
#     """

#     voltage = station.get("voltage")

#     if voltage == "110000":
#         voltage = "110 kV"
#     elif voltage == "220000":
#         voltage = "220 kV"
#     elif voltage == "380000":
#         voltage = "380 kV"

#     voltage = voltage or ""

#     if "380000" in voltage:
#         return SUBSTATION_380KV

#     if "220000" in voltage:
#         return SUBSTATION_220KV

#     return SUBSTATION_110KV

def _get_color(voltage: str | None) -> list[int]:

    voltage = str(voltage or "")

    if "380000" in voltage:
        return SUBSTATION_380KV

    if "220000" in voltage:
        return SUBSTATION_220KV

    return SUBSTATION_110KV

def _format_voltage(voltage):

    voltage = str(voltage or "")

    if "380000" in voltage:
        return "380 kV"

    if "220000" in voltage:
        return "220 kV"

    if "110000" in voltage:
        return "110 kV"

    return "-"

def build_substation_layer(
    substations,
) -> pdk.Layer:
    """
    Returns the High Voltage Substation layer.
    """

    if not substations:
        return None

    data = []

    for station in substations:

        if hasattr(station, "_mapping"):
            station = dict(station._mapping)
        else:
            station = dict(station)

        data.append(
            {
                "id": station.get("id"),
                "name": station.get("name") or "HV Substation",
                "company": station.get("operator") or "Grid Operator",
                "operator": station.get("operator") or "-",
                "city": station.get("city") or "-",
                "voltage": _format_voltage(
                    station.get("voltage")
                ),
                "latitude": station.get("latitude"),
                "longitude": station.get("longitude"),
                "color": _get_color(
                    station.get("voltage")
                ),
            }
        )

    return pdk.Layer(
        "ScatterplotLayer",

        id="substations",

        data=data,

        get_position="[longitude, latitude]",

        get_fill_color="color",

        get_radius=SUBSTATION_RADIUS,

        get_line_color=[255,255,255],

        line_width_min_pixels=2,

        stroked=True,
        filled=True,

        pickable=True,
        auto_highlight=True,

        opacity=0.90,

        radius_min_pixels=7,
        radius_max_pixels=18,

        highlight_color=[255,215,0,255],
    )