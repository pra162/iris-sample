"""
AI Workspace Header

Renders the header section of the
AI Infrastructure Advisor.

Author:
NRW BI Platform
"""

from __future__ import annotations

import streamlit as st


# ==========================================================
# Header
# ==========================================================
def render_ai_header() -> None:

    with st.container(key="ai_header"):

        left, right = st.columns(
            [8, 2],
            vertical_alignment="center",
        )

        with left:
            st.markdown(
                "##### 🤖 AI Infrastructure Advisor"
            )

        with right:
            st.markdown(
                """
<div style="text-align:right;
font-size:12px;
color:#16A34A;
font-weight:600;">
🟢 Connected
</div>
""",
                unsafe_allow_html=True,
            )