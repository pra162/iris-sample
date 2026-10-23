import streamlit as st

def render_header():
    left, right = st.columns([5.5, 1.8], gap="medium", vertical_alignment="center")

    with left:
        st.html("""
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="display: inline-block; width: 7px; height: 7px; background-color: #16A34A; border-radius: 50%;"></span>
                    <span style="font-size: 11px; font-weight: 700; color: #16A34A; text-transform: uppercase; letter-spacing: 0.08em;">Live Intelligence System</span>
                </div>
                <div style="font-size: 22px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; line-height: 1.2;">NRW Data Center & Infrastructure Intelligence</div>
                <div style="font-size: 13px; font-weight: 500; color: #64748B; margin-top: 3px;">North Rhine-Westphalia, Germany • Regional Site Suitability & Analytics</div>
            </div>
        """)