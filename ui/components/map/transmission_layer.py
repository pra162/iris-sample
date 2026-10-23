"""
Transmission Layer

Responsible for rendering all High Voltage
Transmission Lines on the map.

This module contains NO business logic.
"""

import folium

from .map_styles import (
    LINE_110KV_COLOR,
    LINE_220KV_COLOR,
    LINE_380KV_COLOR,
    LINE_110KV_WEIGHT,
    LINE_220KV_WEIGHT,
    LINE_380KV_WEIGHT,
    LINE_OPACITY,
)


# ==========================================================
# Helpers
# ==========================================================

def _line_style(voltage: str | None) -> dict:
    """
    Returns line styling based on voltage.
    """

    voltage = voltage or ""

    if "380000" in voltage:
        return {
            "color": LINE_380KV_COLOR,
            "weight": LINE_380KV_WEIGHT,
        }

    if "220000" in voltage:
        return {
            "color": LINE_220KV_COLOR,
            "weight": LINE_220KV_WEIGHT,
        }

    return {
        "color": LINE_110KV_COLOR,
        "weight": LINE_110KV_WEIGHT,
    }


# ==========================================================
# Public API
# ==========================================================

def add_transmission_lines(
    m: folium.Map,
    high_voltage_lines: list[dict],
) -> None:
    """
    Adds all transmission lines to the map.
    """

    if not high_voltage_lines:
        return

    layer = folium.FeatureGroup(
        name="⚡ Transmission Network",
        show=True,
    )

    for line in high_voltage_lines:

        geometry = line.get("geometry")

        if geometry is None:
            continue

        style = _line_style(
            line.get("voltage"),
        )

        popup = folium.Popup(
            f"""
            <b>Transmission Line</b><br>
            <b>Name:</b> {line.get("name") or "-"}<br>
            <b>Voltage:</b> {line.get("voltage") or "-"}<br>
            <b>Operator:</b> {line.get("operator") or "-"}
            """,
            max_width=260,
        )

        folium.GeoJson(
            data=geometry,
            style_function=lambda _, s=style: {
                "color": s["color"],
                "weight": s["weight"],
                "opacity": LINE_OPACITY,
            },
            popup=popup,
        ).add_to(layer)

    layer.add_to(m)