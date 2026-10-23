"""
Site Score Panel

Responsible for rendering the overall
Site Intelligence Score.
"""

import streamlit as st


def render_site_score(site_score: dict | None):
    """
    Renders the Site Intelligence Score card and the breakdown container
    with customized colors for each individual element.
    """

    if not site_score:
        st.info("No score available.")
        return

    overall = site_score["overall_score"]
    rating = site_score["rating"]

    # 1. Overall Score Card
    st.markdown(
        f"""<div style="
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:12px;
            padding:20px;
            margin-bottom:20px;
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">
                <div>
                    <div style="
                        font-size:13px;
                        color:#2563EB;
                        font-weight:600;
                        text-transform:uppercase;
                        letter-spacing:1px;
                    ">
                        Site Intelligence Score
                    </div>
                    <div style="
                        font-size:34px;
                        font-weight:700;
                        color:#0F172A;
                        margin-top:6px;
                    ">
                        {overall} / 100
                    </div>
                    <div style="
                        color:#64748B;
                        margin-top:4px;
                        font-size:15px;
                    ">
                        {rating}
                    </div>
                </div>
                <div style="
                    width:90px;
                    height:90px;
                    border-radius:50%;
                    border:6px solid #2563EB;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    font-size:26px;
                    font-weight:700;
                    color:#2563EB;
                ">
                    {overall}
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    print(site_score)
    # 2. Build items HTML with unique colors for each progress bar and accent
    grid_html = _get_progress_html("⚡ Grid Infrastructure", site_score["grid_score"], 25, "#2563EB")
    trans_html = _get_progress_html("📡 Transmission Network", site_score["transmission_score"], 20, "#7C3AED")
    transformer_html = _get_progress_html("🔌 Transformer Access", site_score["transformer_score"], 15, "#0D9488")
    renewable_html = _get_progress_html("☀ Renewable Energy", site_score["renewable_score"], 10, "#D97706")
    land_html = _get_progress_html("💰 Land Value", site_score["land_score"], 15, "#16A34A")
    expansion_html = _get_progress_html("🏗 Expansion Potential", site_score["expansion_score"], 15, "#DB2777")

    # Render the entire breakdown card in one single st.markdown call
    st.markdown(
        f"""<div style="
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:12px;
            padding:20px;
            margin-bottom:20px;
        ">
            {grid_html}
            {trans_html}
            {transformer_html}
            {renewable_html}
            {land_html}
            {expansion_html}
        </div>""",
        unsafe_allow_html=True,
    )


def _get_progress_html(title, value, maximum, color):
    percent = int((value / maximum) * 100) if maximum > 0 else 0
    return f"""<div style="margin-bottom:16px;">
        <div style="
            display:flex;
            justify-content:space-between;
            font-size:14px;
            margin-bottom:6px;
            font-weight:600;
            color:#0F172A;
        ">
            <span style="color:{color};">{title}</span>
            <span><b style="color:{color};">{value}</b> / {maximum}</span>
        </div>
        <div style="
            background:#E2E8F0;
            border-radius:8px;
            height:10px;
            width:100%;
            overflow:hidden;
        ">
            <div style="
                width:{percent}%;
                height:10px;
                background:{color};
                border-radius:8px;
            ">
            </div>
        </div>
    </div>"""