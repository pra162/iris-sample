import pandas as pd
import plotly.express as px
import streamlit as st
import html


def render_ranking_table(rankings):
    html_content = (
        '<div class="panel" style="padding: 20px; height: 100%; background: white; border-radius: 18px; box-shadow: 0 3px 12px rgba(0,0,0,.08);">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
        '<div style="font-size: 20px; font-weight: 700; color: #111827;">Top Ranked Sites</div>'
        '<a href="#" style="font-size: 13px; color: #2563EB; text-decoration: none; font-weight: 600;">View All</a>'
        "</div>"
        "<style>"
        '[data-testid="stDataFrame"] { background-color: white !important; border: none !important; }'
        '[data-testid="stDataFrame"] table { background-color: white !important; color: #111827 !important; }'
        '[data-testid="stDataFrame"] th { background-color: #F8FAFC !important; color: #111827 !important; font-weight: 600 !important; border-bottom: 1px solid #E2E8F0 !important; }'
        '[data-testid="stDataFrame"] td { background-color: white !important; color: #334155 !important; border-bottom: 1px solid #F1F5F9 !important; }'
        "</style>"
    )
    st.markdown(html_content, unsafe_allow_html=True)

    data = pd.DataFrame(
    [
        {
            "Rank": index + 1,
            "Facility": site.get("facility_name", "-"),
            "City": site.get("city", "-"),
            "Operator": site.get("company", "-"),
            "Score": round(site.get("overall_score", 0), 1),
            "Grid": round(site.get("grid_score", 0), 1),
            "Transmission": round(site.get("transmission_score", 0), 1),
            "Land €/m²": site.get("land_value", "-"),
        }
        for index, site in enumerate(rankings)
    ]
)

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        height=245,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_panel():
    st.markdown(
        '<div class="panel" style="padding: 20px; height: 100%; background: white; border-radius: 18px; box-shadow: 0 3px 12px rgba(0,0,0,.08);">'
        '<div style="font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 12px;">Site Score Distribution</div>',
        unsafe_allow_html=True,
    )

    score_data = pd.DataFrame(
        {
            "Category": [
                "80 - 100 (Excellent)",
                "60 - 80 (Good)",
                "40 - 60 (Average)",
                "20 - 40 (Poor)",
                "0 - 20 (Very Poor)",
            ],
            "Count": [28, 34, 22, 10, 6],
        }
    )

    fig = px.pie(
        score_data,
        values="Count",
        names="Category",
        hole=0.62,
        color_discrete_sequence=[
            "#16A34A",
            "#2563EB",
            "#FBBF24",
            "#F97316",
            "#DC2626",
        ],
    )

    fig.add_annotation(
        text="<b>592</b><br><span style='font-size:11px; color:#64748B;'>Total Sites</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=15, color="#111827", family="Segoe UI"),
    )

    fig.update_layout(
        height=210,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            x=1.02,
            font=dict(size=11, color="#334155"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center;">'
        '<div style="font-size: 13px; color: #64748B; font-weight: 600;">Evaluation Coverage</div>'
        '<div style="font-size: 13px; color: #16A34A; font-weight: 700;">100% Analyzed</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

def render_market_intelligence(news):
    print(news)
  
    html_content = """
    <div class="panel" style="
        padding:16px;
        background:white;
        border-radius:14px;
        box-shadow:0 2px 8px rgba(0,0,0,.08);
    ">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:15px;
    ">

        <div style="
            font-size:18px;
            font-weight:700;
            color:#111827;
        ">
            Latest News Signals
        </div>

        <span style="
            color:#2563EB;
            font-size:13px;
            font-weight:600;
        ">
            {count} Articles
        </span>

    </div>
    """.format(count=len(news))

    for article in news:

        company = html.escape(article.get("company") or "Unknown")
        title = html.escape(article.get("title") or "")
        city = html.escape(article.get("city") or "")
        published = html.escape(str(article.get("published") or ""))
        match_type = html.escape(article.get("match_type") or "News")
        summary = html.escape(article.get("summary") or "")

        html_content += f"""
        <div style="
            border:1px solid #E5E7EB;
            border-radius:10px;
            padding:10px;
            margin-bottom:10px;
            background:#fff;
        ">

            <div style="
                font-size:11px;
                font-weight:700;
                color:#2563EB;
                margin-bottom:4px;
            ">
                {company}
            </div>

            <div style="
                font-size:13px;
                font-weight:600;
                color:#111827;
                line-height:1.35;
                margin-bottom:8px;
            ">
                {title}
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                font-size:11px;
                color:#6B7280;
            ">

                <span>{city}</span>

                <span>{published}</span>

            </div>

            <div style="
                margin-top:8px;
            ">

                <span style="
                    background:#EFF6FF;
                    color:#2563EB;
                    padding:3px 8px;
                    border-radius:6px;
                    font-size:10px;
                    font-weight:600;
                ">
                    {match_type}
                </span>

            </div>

            <div style="
                margin-top:8px;
            ">

                <span style="
                    background:#EFF6FF;
                    color:#2563EB;
                    padding:3px 8px;
                    border-radius:6px;
                    font-size:10px;
                    font-weight:600;
                ">
                    {summary}
                </span>

            </div>

        </div>
        """

    html_content += "</div>"

    # st.markdown(
    #     html_content,
    #     unsafe_allow_html=True,
    # )

    st.html(html_content)