import streamlit as st
import plotly.express as px
import pandas as pd

def render_city_charts():
    # Data for Sites by City
    sites_data = pd.DataFrame({
        "City": ["Cologne", "Düsseldorf", "Dortmund", "Essen", "Münster", "Bielefeld", "Aachen", "Bonn", "Paderborn"],
        "Sites": [120, 98, 76, 65, 42, 31, 28, 24, 18]
    })

    # Data for Average Land Value (€/m²) by City
    land_data = pd.DataFrame({
        "City": ["Cologne", "Düsseldorf", "Essen", "Dortmund", "Münster", "Bielefeld", "Aachen", "Paderborn", "Bonn"],
        "LandValue": [142, 135, 120, 105, 98, 85, 80, 75, 70]
    })

    # Create figure for Sites by City with professional styling and narrower bars
    fig_sites = px.bar(
        sites_data,
        x="City",
        y="Sites",
        text="Sites",
        color_discrete_sequence=["#2563EB"]
    )
    fig_sites.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="#0F172A", family="Segoe UI"),
        width=0.55  # Reduced bar width
    )
    fig_sites.update_layout(
        title=dict(
            text="<b>Sites by City</b>", 
            font=dict(size=13, color="#0F172A"),
            x=0.02,  # Left padding offset for title
            y=0.92   # Top padding offset for title
        ),
        height=240,
        margin=dict(l=15, r=15, t=50, b=15),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 150], tickfont=dict(size=9)),
        showlegend=False
    )

    # Create figure for Average Land Value by City with professional styling and narrower bars
    fig_land = px.bar(
        land_data,
        x="City",
        y="LandValue",
        text=land_data["LandValue"].apply(lambda x: f"€{x}"),
        color_discrete_sequence=["#16A34A"]
    )
    fig_land.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="#0F172A", family="Segoe UI"),
        width=0.55  # Reduced bar width
    )
    fig_land.update_layout(
        title=dict(
            text="<b>Average Land Value (€/m²) by City</b>", 
            font=dict(size=13, color="#0F172A"),
            x=0.02,  # Left padding offset for title
            y=0.92   # Top padding offset for title
        ),
        height=240,
        margin=dict(l=15, r=15, t=50, b=15),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 200], tickfont=dict(size=9)),
        showlegend=False
    )

    # Render side by side using columns with container boxes and professional inner padding
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown('<div style="padding: 4px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_sites, width="stretch", config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container(border=True):
            st.markdown('<div style="padding: 4px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_land, width="stretch", config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)