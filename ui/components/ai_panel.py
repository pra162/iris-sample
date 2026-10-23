from __future__ import annotations

import html
import textwrap

import streamlit as st
import streamlit.components.v1 as components

from app.database.session import SessionLocal
from app.services.dashboard_service import DashboardService
from app.services.ai_recommendation_service import (
    AIRecommendationService,
)
from app.services.ai_advisor_service import AIAdvisorService


# ============================================================
# Helpers
# ============================================================

def _html(raw: str):
    st.markdown(
        textwrap.dedent(raw).strip(),
        unsafe_allow_html=True,
    )


def render_message(role, content, sources=None):
    escaped_content = html.escape(content).replace("\n", "<br>")
    source_html = ""
    if sources:
        source_html = (
            "<div class='chat-source-row'>"
            "<span class='chat-source-label'>Sources &middot; " + ", ".join(sources) + "</span>"
            "<span class='chat-source-actions'>"
            "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
            "stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
            "<path d='M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z'/>"
            "</svg>"
            "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
            "stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
            "<path d='M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z'/>"
            "</svg>"
            "</span>"
            "</div>"
        )

    if role == "assistant":
        return f"""
<div class="chat-row assistant">
    <div class="chat-block assistant">
        <div class="role-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="9"/>
                <path d="M12 3a4 4 0 0 0-4 4c0 1.5.8 2.3 1.5 3-1 .3-2 1.3-2 3a3 3 0 0 0 3 3"/>
            </svg>
            Advisor
        </div>
        <div class="bubble-content">
            {escaped_content}
        </div>
        {source_html}
    </div>
</div>
"""

    return f"""
<div class="chat-row user">
    <div class="chat-bubble user">
        <div class="bubble-content">
            {escaped_content}
        </div>
    </div>
</div>
"""


def render_typing():
    return """
<div class="chat-row assistant">
    <div class="chat-block assistant typing-block">
        <div class="role-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="9"/>
                <path d="M12 3a4 4 0 0 0-4 4c0 1.5.8 2.3 1.5 3-1 .3-2 1.3-2 3a3 3 0 0 0 3 3"/>
            </svg>
            Advisor
        </div>
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
</div>
"""

# ============================================================
# AI PANEL
# ============================================================

def render_ai_panel():

    # --------------------------------------------------------
    # Session State
    # --------------------------------------------------------

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Welcome to AI Infrastructure Advisor.\n"
                    "I can analyze the selected Data Center. Try asking:\n"
                    "• Analyze this site\n"
                    "• Explain the Site Score\n"
                    "• Biggest risks?"
                ),
            }
        ]

    if "ai_pending" not in st.session_state:
        st.session_state.ai_pending = False

    # ============================================================
    # AI PANEL CONTAINER WRAPPER
    # ============================================================

 
    with st.container(key="ai_panel"):
        # --------------------------------------------------------
        # Header + Chat Area
        # --------------------------------------------------------

        message_html = [
            render_message(
                message["role"],
                message["content"],
                message.get("sources"),
            )
            for message in st.session_state.ai_messages
        ]

        if st.session_state.ai_pending:
            message_html.append(render_typing())

        chat_html = """
<style>
* { box-sizing: border-box; }
.ai-panel-shell {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Inter, sans-serif;
  background: #FFFFFF;
  border-radius: 14px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
  overflow: hidden;
}
.ai-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 18px;
  border-bottom: 1px solid #E2E8F0;
  background: #FAFBFC;
}
.ai-panel-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-panel-logo {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #F1F5F9;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ai-panel-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ai-panel-title-text {
  font-size: 13.5px;
  font-weight: 600;
  color: #0F172A;
  letter-spacing: 0.1px;
}
.ai-panel-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: #64748B;
  font-weight: 500;
}
.ai-panel-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22C55E;
}
.ai-panel-header-right {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #94A3B8;
}
.ai-chat-area {
  max-height: 320px;
  min-height: 220px;
  overflow-y: auto;
  padding: 20px 18px;
  background: #FFFFFF;
}
.ai-chat-area::-webkit-scrollbar {
  width: 8px;
}
.ai-chat-area::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.45);
  border-radius: 999px;
}
.chat-row {
  display: flex;
  margin-bottom: 20px;
  width: 100%;
  align-items: flex-start;
}
.chat-row.user { justify-content: flex-end; }
.chat-row.assistant { justify-content: flex-start; }

/* Assistant messages: flat, accent-bordered text block (no card) */
.chat-block {
  max-width: 88%;
  width: 100%;
}
.chat-block.assistant {
  padding: 2px 0 2px 14px;
  border-left: 3px solid #2563EB;
}
.chat-block .role-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  color: #64748B;
  text-transform: uppercase;
}
.chat-block .bubble-content {
  font-size: 14px;
  line-height: 1.65;
  color: #1E293B;
}

/* User messages: compact neutral box */
.chat-bubble {
  max-width: 68%;
  border-radius: 10px;
  padding: 10px 14px;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
}
.chat-bubble.user {
  background: #F1F5F9;
  color: #0F172A;
  border: 1px solid #E2E8F0;
}
.chat-bubble.user .bubble-content {
  color: #0F172A;
}

.bubble-content { white-space: pre-wrap; }
.chat-source-row {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.chat-source-label {
  font-size: 11.5px;
  color: #94A3B8;
  letter-spacing: 0.1px;
}
.chat-source-actions {
  display: flex;
  gap: 10px;
  color: #CBD5E1;
  flex-shrink: 0;
}
.typing { display: flex; align-items: center; gap: 6px; padding: 2px 0; }
.typing span { width: 5px; height: 5px; background: #2563EB; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0.5); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
</style>
<div class="ai-panel-shell">
    <div class="ai-panel-header">
        <div class="ai-panel-header-left">
            <div class="ai-panel-logo">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="M12 3a4 4 0 0 0-4 4c0 1.5.8 2.3 1.5 3-1 .3-2 1.3-2 3a3 3 0 0 0 3 3"/>
                </svg>
            </div>
            <div class="ai-panel-title">
                <span class="ai-panel-title-text">AI Infrastructure Advisor</span>
                <span class="ai-panel-status"><span class="ai-panel-status-dot"></span>Online</span>
            </div>
        </div>
        <div class="ai-panel-header-right">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/></svg>
        </div>
    </div>
    <div id='ai-chat-area' class='ai-chat-area'>
"""
        chat_html += "\n".join(message_html)
        chat_html += """
    </div>
</div>
<script>
const chatArea = document.getElementById('ai-chat-area');
if (chatArea) { chatArea.scrollTop = chatArea.scrollHeight; }
</script>
"""

        components.html(
            chat_html,
            height=430,
            scrolling=False,
        )

        # --------------------------------------------------------
        # Footer / Input Form
        # --------------------------------------------------------

        st.markdown(
            """
<style>
div[data-testid="stForm"] {
    border: none !important;
    padding: 12px 6px 4px 6px !important;
}
div[data-testid="stForm"] div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    padding: 10px 14px !important;
    background: #FAFBFC !important;
    font-size: 13.5px !important;
}
div[data-testid="stForm"] button {
    border-radius: 8px !important;
    background: #1E293B !important;
    color: #FFFFFF !important;
    border: none !important;
    height: 42px !important;
}
</style>
""",
            unsafe_allow_html=True,
        )

        with st.form(
            "ai_chat_form",
            clear_on_submit=True,
            border=False,
        ):
            left, right = st.columns(
                [6, 1],
                gap="small",
            )

            with left:
                prompt = st.text_input(
                    "Ask",
                    placeholder="Ask about data center...",
                    label_visibility="collapsed",
                )

            with right:
                submitted = st.form_submit_button(
                    "➤",
                    use_container_width=True,
                )

        st.markdown(
            "<div style='text-align:center; font-size:11px; color:#94A3B8; "
            "margin-top:2px;'>AI responses can make mistakes</div>",
            unsafe_allow_html=True,
        )

 

    # --------------------------------------------------------
    # User submits logic
    # --------------------------------------------------------

    if (
        submitted
        and prompt
        and prompt.strip()
    ):
        st.session_state.ai_messages.append(
            {
                "role": "user",
                "content": prompt.strip(),
            }
        )
        st.session_state.ai_pending = True
        st.rerun()

    # --------------------------------------------------------
    # Waiting for AI check
    # --------------------------------------------------------

    if not st.session_state.ai_pending:
        return

    facility_id = st.session_state.get(
        "selected_facility_id"
    )

    if not facility_id:
        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": "⚠️ Please select a Data Center on the map first.",
            }
        )
        st.session_state.ai_pending = False
        st.rerun()

    # --------------------------------------------------------
    # AI Processing
    # --------------------------------------------------------

    session = SessionLocal()

    try:
        advisor = AIAdvisorService(session)

        result = advisor.ask(
            question=prompt.strip(),
            selected_facility_id=facility_id,
        )

        # --------------------------------------------------------
        # Format AI Response Cards
        # --------------------------------------------------------

        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": result,
                "sources": [
                    "AI Infrastructure Advisor",
                ],
            }
        )


    except Exception as e:
            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "AI Error: "
                        + str(e)
                    ),
                }
            )
    finally:
        session.close()

    st.session_state.ai_pending = False
    st.rerun()