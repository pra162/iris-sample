"""
AI Workspace Chat

Responsible for rendering the AI conversation.

Author:
NRW BI Platform
"""

from __future__ import annotations

import streamlit as st

from ui.components.ai.ai_state import messages


# ==========================================================
# Chat
# ==========================================================

def render_ai_chat() -> str | None:
    """
    Render the AI conversation.
    """

    chat_messages = messages()

    user_messages = [
        message
        for message in chat_messages
        if message["role"] == "user"
    ]

    # ------------------------------------------------------
    # Conversation
    # ------------------------------------------------------

    with st.container(height=320):

        if not user_messages:

            st.markdown(
                """
#### 👋 Welcome

Ask me anything about your Data Center Business Intelligence.

**Examples**

- Analyze this site
- Show data centers in Berlin
- Compare Microsoft vs Equinix
- Top 10 data centers
"""
            )

            st.divider()

        for message in chat_messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

                if message.get("sources"):

                    st.caption(
                        "📚 "
                        + ", ".join(message["sources"])
                    )

        if st.session_state.ai_pending:

            with st.chat_message("assistant"):

                st.status(
                    "AI Assistant is typing...",
                    expanded=False,
                )

    # ------------------------------------------------------
    # Input
    # ------------------------------------------------------

    return st.chat_input(
        "Ask about infrastructure..."
    )