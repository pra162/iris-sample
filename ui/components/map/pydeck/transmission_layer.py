"""
Transmission Layer

Responsible for rendering High Voltage
Transmission Lines using PyDeck.
"""

import json

import pydeck as pdk

from .map_styles import (
    LINE_110KV,
    LINE_220KV,
    LINE_380KV,
)


# ==========================================================
# Helpers
# ==========================================================

def _get_color(voltage: str |None) -> list[int]:
    """
    Returns RGB color based on voltage.
    """

    voltage = voltage or ""

    if "380000" in voltage:
        return LINE_380KV

    if "220000" in voltage:
        return LINE_220KV

    return LINE_110KV


# ==========================================================
# Public API
# ==========================================================

def build_transmission_layer(
    high_voltage_lines: list[dict],
) -> pdk.Layer:
    """
    Returns the Transmission Network layer.
    """

    if not high_voltage_lines:
        return None

    data = []

    for line in high_voltage_lines:

        geometry = line.get("geometry")

        if geometry is None:
            continue

        # Convert GeoJSON string -> Python object
        if isinstance(geometry, str):
            geometry = json.loads(geometry)

        if geometry["type"] != "LineString":
            continue

        data.append({
            "path": geometry["coordinates"],
            "color": _get_color(line.get("voltage")),
            "name": line.get("name"),
            "voltage": line.get("voltage"),
            "operator": line.get("operator"),
        })

    return pdk.Layer(
        "PathLayer",

        data=data,

        get_path="path",

        get_color="color",

        width_scale=1,

        width_min_pixels=2,

        get_width=4,

        pickable=True,

        auto_highlight=True,
    )