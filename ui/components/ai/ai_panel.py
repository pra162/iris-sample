"""
AI Workspace

Main AI workspace for the
AI Infrastructure Advisor.

Author:
NRW BI Platform
"""

from __future__ import annotations

import streamlit as st

from app.database.session import SessionLocal
from app.services.ai_advisor_service import AIAdvisorService

from ui.components.ai.ai_state import (
    initialize_ai_state,
    add_user_message,
    add_assistant_message,
    set_pending,
)

from ui.components.ai.ai_header import (
    render_ai_header,
)

from ui.components.ai.ai_chat import (
    render_ai_chat,
)


# ==========================================================
# Public
# ==========================================================

def render_ai_panel() -> None:

    initialize_ai_state()

    with st.container(
        border=True,
        key="ai_workspace",
    ):

        render_ai_header()

        prompt = render_ai_chat()

    # --------------------------------------------
    # New Prompt
    # --------------------------------------------

    if (
        prompt
        and prompt.strip()
    ):

        add_user_message(
            prompt.strip(),
        )

        st.session_state.ai_current_prompt = (
            prompt.strip()
        )

        set_pending(True)

        st.rerun()

    # --------------------------------------------
    # Pending Request
    # --------------------------------------------

    if not st.session_state.ai_pending:
        return

    facility_id = st.session_state.get(
        "selected_facility_id"
    )

    if facility_id is None:

        add_assistant_message(
            "⚠️ Please select a Data Center on the map first."
        )

        st.session_state.ai_current_prompt = None

        set_pending(False)

        st.rerun()

    prompt = st.session_state.ai_current_prompt

    response = _call_ai(
        question=prompt,
        facility_id=facility_id,
    )

    add_assistant_message(
        response,
        ["AI Infrastructure Advisor"],
    )

    st.session_state.ai_current_prompt = None

    set_pending(False)

    st.rerun()


# ==========================================================
# AI
# ==========================================================

def _call_ai(
    question: str,
    facility_id: int,
) -> str:

    session = SessionLocal()

    try:

        advisor = AIAdvisorService(
            session,
        )

        return advisor.ask(
            question=question,
            selected_facility_id=facility_id,
        )

    except Exception as exc:

        return (
            f"AI Error: {exc}"
        )

    finally:

        session.close()

        