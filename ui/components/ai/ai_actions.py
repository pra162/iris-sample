"""
AI Workspace Actions

Quick action toolbar for the
AI Infrastructure Advisor.

Author:
NRW BI Platform
"""

from __future__ import annotations

import streamlit as st


# ==========================================================
# Quick Actions
# ==========================================================

def render_ai_actions() -> str | None:
    """
    Render compact quick action buttons.

    Returns:
        Selected prompt or None.
    """

    st.caption("Quick Actions")

    row1 = st.columns(3)
    row2 = st.columns(3)

    # ------------------------------------------------------
    # Row 1
    # ------------------------------------------------------

    with row1[0]:
        if st.button(
            "🔍 Analyze",
            use_container_width=True,
        ):
            return "Analyze the selected site"

    with row1[1]:
        if st.button(
            "📊 Ranking",
            use_container_width=True,
        ):
            return "Top 10 data centers"

    with row1[2]:
        if st.button(
            "🏢 Compare",
            use_container_width=True,
        ):
            return "Compare Microsoft vs Equinix"

    # ------------------------------------------------------
    # Row 2
    # ------------------------------------------------------

    with row2[0]:
        if st.button(
            "📍 Nearby",
            use_container_width=True,
        ):
            return "Find nearby data centers"

    with row2[1]:
        if st.button(
            "⚡ Grid",
            use_container_width=True,
        ):
            return "Explain the grid infrastructure"

    with row2[2]:
        if st.button(
            "🌱 Green",
            use_container_width=True,
        ):
            return "Analyze renewable energy"

    return None