import streamlit as st


def render_map_legend():

    st.html("""
    <div style="
        background:white;
        border:1px solid #E5E7EB;
        border-radius:12px;
        padding:14px 24px;
        margin-bottom:12px;
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        box-shadow:0 2px 6px rgba(0,0,0,.08);
        font-family:Inter,sans-serif;
        font-size:14px;
        font-weight:600;
    ">

        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:14px;height:14px;border-radius:50%;background:#2563EB;"></div>
            <span>Data Centers</span>
        </div>

        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:14px;height:14px;border-radius:50%;background:#F97316;"></div>
            <span>HV Substations</span>
        </div>

        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:14px;height:14px;border-radius:50%;background:#A855F7;"></div>
            <span>Transformers</span>
        </div>

        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:14px;height:14px;border-radius:50%;background:#22C55E;"></div>
            <span>Renewable Energy</span>
        </div>

    </div>
    """)