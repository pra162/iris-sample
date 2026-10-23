import streamlit as st
import plotly.express as px
import pandas as pd

def render_analytics_panel():
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

    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=10, color="white", family="Segoe UI"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
    )

    fig.add_annotation(
        text="<b>592</b><br><span style='font-size:9px; color:#64748B;'>Total Sites</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=12, color="#0F172A", family="Segoe UI"),
    )

    # Added margin padding around the donut chart to prevent clipping
    fig.update_layout(
        height=170,
        margin=dict(l=15, r=15, t=10, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; border-bottom: 1px solid #F1F5F9; padding-bottom: 4px;">
                <div style="font-size: 14px; font-weight: 700; color: #0F172A; letter-spacing: -0.01em;">Site Score Distribution</div>
                <div style="font-size: 11px; font-weight: 500; color: #64748B; background: #F8FAFC; padding: 2px 8px; border-radius: 6px; border: 1px solid #E2E8F0;">Live Metrics</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Arranged in 3 compact rows on a white background with tight spacing
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 8px; margin-bottom: 6px; display: flex; flex-direction: column; gap: 4px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10.5px;">
            <!-- Row 1 -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="width: 7px; height: 7px; background: #16A34A; border-radius: 2px; display: inline-block; flex-shrink: 0;"></span>
                    <span style="color: #334155; font-weight: 500;">80-100 (Excellent): <strong style="color: #0F172A;">28</strong></span>
                </div>
            </div>
            <!-- Row 2 -->
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="width: 7px; height: 7px; background: #2563EB; border-radius: 2px; display: inline-block; flex-shrink: 0;"></span>
                    <span style="color: #334155; font-weight: 500;">60-80 (Good): <strong style="color: #0F172A;">34</strong></span>
                </div>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="width: 7px; height: 7px; background: #FBBF24; border-radius: 2px; display: inline-block; flex-shrink: 0;"></span>
                    <span style="color: #334155; font-weight: 500;">40-60 (Average): <strong style="color: #0F172A;">22</strong></span>
                </div>
            </div>
            <!-- Row 3 -->
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="width: 7px; height: 7px; background: #F97316; border-radius: 2px; display: inline-block; flex-shrink: 0;"></span>
                    <span style="color: #334155; font-weight: 500;">20-40 (Poor): <strong style="color: #0F172A;">10</strong></span>
                </div>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span style="width: 7px; height: 7px; background: #DC2626; border-radius: 2px; display: inline-block; flex-shrink: 0;"></span>
                    <span style="color: #334155; font-weight: 500;">0-20 (Very Poor): <strong style="color: #0F172A;">6</strong></span>
                </div>
            </div>
        </div>
        """)

        # Wrapped chart in a padded container for clean separation
        st.markdown('<div style="padding: 4px 0;">', unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)