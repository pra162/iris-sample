"""
AI Workspace Sidebar

Displays the current infrastructure intelligence
for the selected facility.

Author:
NRW BI Platform
"""

from __future__ import annotations

import streamlit as st

from app.database.session import SessionLocal
from app.services.dashboard_service import DashboardService


# ==========================================================
# Sidebar
# ==========================================================

def render_ai_sidebar() -> None:
    """
    Render the intelligence sidebar.
    """

    facility_id = st.session_state.get(
        "selected_facility_id"
    )

    with st.container(height=400):

        with st.container(border=True):

            st.markdown("#### 📊 Intelligence")

            # --------------------------------------------------
            # No Selection
            # --------------------------------------------------

            if not facility_id:

                st.info(
                    "Select a Data Center to begin analysis."
                )

                return

            session = SessionLocal()

            try:

                dashboard = DashboardService(
                    session
                )

                intelligence = (
                    dashboard.get_site_intelligence(
                        facility_id
                    )
                )

            finally:

                session.close()

            if intelligence is None:

                st.warning(
                    "No intelligence available."
                )

                return

            facility = intelligence["facility"]
            score = intelligence["site_score"]

            # --------------------------------------------------
            # Facility
            # --------------------------------------------------

            st.caption("Selected Facility")

            st.markdown(
                f"**{facility.name}**"
            )

            st.caption(
                f"{facility.company}"
            )

            st.caption(
                f"{facility.city}, {facility.country}"
            )

            st.divider()

            # --------------------------------------------------
            # Overall Score
            # --------------------------------------------------

            st.metric(
                "Site Score",
                score["overall_score"],
            )

            st.caption(
                score["rating"]
            )

            st.divider()

            # --------------------------------------------------
            # Infrastructure
            # --------------------------------------------------

            st.caption("Infrastructure")

            left, right = st.columns(2)

            with left:

                st.metric(
                    "Grid",
                    score["grid_score"],
                )

                st.metric(
                    "Transformer",
                    score["transformer_score"],
                )

                st.metric(
                    "Land",
                    score["land_score"],
                )

            with right:

                st.metric(
                    "Transmission",
                    score["transmission_score"],
                )

                st.metric(
                    "Renewable",
                    score["renewable_score"],
                )

                st.metric(
                    "Expansion",
                    score["expansion_score"],
                )

            st.divider()

            st.success(
                "Ready for Analysis"
            )