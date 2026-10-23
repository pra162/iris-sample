import streamlit as st


def render_map_legend():

    st.markdown(
        """
<div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:10px 15px;margin-top:8px;margin-bottom:4px;">

<div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;color:#111827;font-size:13px;">

<div><strong>🗺️ Map Legend</strong></div>

<div>
<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#2563EB;"></span>
&nbsp;Data Centers
</div>

<div>
<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#DC2626;"></span>
&nbsp;HV Substations
</div>

<div>
<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#7C3AED;"></span>
&nbsp;Transformers
</div>

<div>
<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#16A34A;"></span>
&nbsp;Renewables
</div>

<div>
<span style="display:inline-block;width:24px;height:3px;background:#2563EB;"></span>
&nbsp;110 kV
</div>

<div>
<span style="display:inline-block;width:24px;height:3px;background:#F59E0B;"></span>
&nbsp;220 kV
</div>

<div>
<span style="display:inline-block;width:24px;height:3px;background:#DC2626;"></span>
&nbsp;380 kV
</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )