"""
Layer Panel

Responsible for rendering the Infrastructure Layer
controls for the PyDeck map.
"""

import streamlit as st


def render_layer_panel() -> dict:
    """
    Renders the infrastructure layer controls.

    Returns:
        dict containing all enabled layers.
    """

    with st.container(border=True):

        st.markdown("### 🗂 Layers")

        show_facilities = st.toggle("🏢 DC", True)
        show_substations = st.toggle("⚡ HV", True)
        show_transformers = st.toggle("🔌 TR", True)
        show_transmission = st.toggle("📡 Line", True)
        show_energy = st.toggle("☀ RE", True)

    return {
        "show_facilities": show_facilities,
        "show_substations": show_substations,
        "show_transformers": show_transformers,
        "show_transmission": show_transmission,
        "show_energy": show_energy,
    }