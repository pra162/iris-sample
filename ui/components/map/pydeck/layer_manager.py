"""
Layer Manager

Responsible for assembling all PyDeck layers.
"""

import pydeck as pdk

from .energy_layer import build_energy_layer
from .facility_layer import build_facility_layer
from .substation_layer import build_substation_layer
from .transformer_layer import build_transformer_layer
from .transmission_layer import build_transmission_layer


def build_layers(
    facilities: list[dict],
    substations: list[dict],
    transformers: list[dict],
    high_voltage_lines: list[dict],
    energy_assets: list[dict],
    show_facilities: bool = True,
    show_substations: bool = True,
    show_transformers: bool = True,
    show_transmission: bool = True,
    show_energy: bool = True,
) -> list[pdk.Layer]:
    """
    Builds and returns all enabled PyDeck layers.
    """

    layers: list[pdk.Layer] = []

    if show_transmission:
        layer = build_transmission_layer(high_voltage_lines)
        if layer is not None:
            layers.append(layer)

    if show_substations:
        layer = build_substation_layer(substations)
        if layer is not None:
            layers.append(layer)

    if show_transformers:
        layer = build_transformer_layer(transformers)
        if layer is not None:
            layers.append(layer)

    if show_facilities:
        layer = build_facility_layer(facilities)
        if layer is not None:
            layers.append(layer)

    if show_energy:
        layer = build_energy_layer(energy_assets)
        if layer is not None:
            layers.append(layer)

    return layers