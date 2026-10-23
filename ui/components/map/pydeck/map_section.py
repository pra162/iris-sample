"""
PyDeck Map Section

Responsible for rendering the complete GIS map.

No business logic.
"""

import streamlit as st

from .layer_manager import build_layers
from .map_builder import build_map


def render_map(
    facilities,
    energy_assets,
    substations,
    high_voltage_lines,
    transformers,
    show_facilities=True,
    show_substations=True,
    show_transformers=True,
    show_transmission=True,
    show_energy=True,
):
    """
    Builds and renders the PyDeck map.
    """

    layers = build_layers(
        facilities=facilities,
        substations=substations,
        transformers=transformers,
        high_voltage_lines=high_voltage_lines,
        energy_assets=energy_assets,
        show_facilities=show_facilities,
        show_substations=show_substations,
        show_transformers=show_transformers,
        show_transmission=show_transmission,
        show_energy=show_energy,
    )

   
    deck = build_map(layers)

    event = st.pydeck_chart(
        deck,
        width="stretch",
        height=500,
        key="nrw-pydeck-map",
        on_select="rerun",
        selection_mode="single-object",
    )

    return event