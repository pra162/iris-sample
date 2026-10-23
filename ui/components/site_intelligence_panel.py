import streamlit as st


def _format_distance(distance):
    if distance is None:
        return "--"
    if distance < 1:
        return f"{distance * 1000:.0f} m"
    return f"{distance:.2f} km"


def _format_voltage(voltage):
    if not voltage:
        return "--"
    if ";" in str(voltage):
        return str(voltage).replace("000", " kV / ").replace(";", " / ") + " kV"
    try:
        return f"{int(voltage)/1000:.0f} kV"
    except Exception:
        return str(voltage)


def _get_distance_badge(distance_km):
    if distance_km is None:
        return '<span style="background: #F1F5F9; color: #64748B; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">No Data</span>'
    if distance_km < 1:
        return '<span style="background: #ECFDF5; color: #047857; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid #A7F3D0;">Optimal</span>'
    elif distance_km < 3:
        return '<span style="background: #FEF3C7; color: #B45309; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid #FDE68A;">Moderate</span>'
    else:
        return '<span style="background: #FEE2E2; color: #B91C1C; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid #FECACA;">Distant</span>'


def render_site_intelligence(intelligence):
    if not intelligence:
        st.warning("No site intelligence data available for the selected location.")
        return

    power = intelligence.get("power", {})
    substation = power.get("nearest_substation")
    hv_line = power.get("nearest_high_voltage_line")
    transformer = power.get("nearest_transformer")
    land = intelligence.get("land", {})
    
    # Header Panel
    st.markdown(
        """
        <div class="si-header-container">
            <div>
                <div class="si-title">🧠 Site Intelligence & Proximity Grid</div>
                <div class="si-subtitle">Real-time infrastructure proximity & capacity assessment</div>
            </div>
            <span style="font-size: 12px; font-weight: 600; color: #2563EB; background: rgba(37,99,235,0.08); padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(37,99,235,0.15);">Live Analysis</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # FOUR CARDS IN A SINGLE ROW: SUBSTATION, HV LINE, TRANSFORMER, LAND INTELLIGENCE
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        sub_d_val = substation.get("distance_km") if substation else None
        sub_dist = _format_distance(sub_d_val)
        sub_volt = _format_voltage(substation.get("voltage")) if substation else "--"
        sub_op = (substation.get("operator") if substation else None) or "Unknown Operator"
        badge = _get_distance_badge(sub_d_val)

        st.markdown(
            f"""
            <div class="enterprise-card">
                <div class="card-header-flex">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="card-icon-box" style="background: #EFF6FF; color: #2563EB;">⚡</div>
                        <span class="metric-title">Substation</span>
                    </div>
                    {badge}
                </div>
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Proximity Distance</div>
                <div class="metric-value-box">{sub_dist}</div>
                <div class="card-divider"></div>
                <div class="meta-row"><span class="meta-key">Voltage Capacity</span><span class="meta-val">{sub_volt}</span></div>
                <div class="meta-row"><span class="meta-key">Operator</span><span class="meta-val" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{sub_op}">{sub_op}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        hv_d_val = hv_line.get("distance_km") if hv_line else None
        hv_dist = _format_distance(hv_d_val)
        hv_volt = _format_voltage(hv_line.get("voltage")) if hv_line else "--"
        hv_op = (hv_line.get("operator") if hv_line else None) or "Unknown Operator"
        badge = _get_distance_badge(hv_d_val)

        st.markdown(
            f"""
            <div class="enterprise-card">
                <div class="card-header-flex">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="card-icon-box" style="background: #FFF7ED; color: #EA580C;">🟠</div>
                        <span class="metric-title">HV Line</span>
                    </div>
                    {badge}
                </div>
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Proximity Distance</div>
                <div class="metric-value-box">{hv_dist}</div>
                <div class="card-divider"></div>
                <div class="meta-row"><span class="meta-key">Voltage Capacity</span><span class="meta-val">{hv_volt}</span></div>
                <div class="meta-row"><span class="meta-key">Operator</span><span class="meta-val" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{hv_op}">{hv_op}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        tr_d_val = transformer.get("distance_km") if transformer else None
        tr_dist = _format_distance(tr_d_val)
        tr_volt = _format_voltage(transformer.get("voltage")) if transformer else "--"
        tr_op = (transformer.get("operator") if transformer else None) or "Unknown Operator"
        badge = _get_distance_badge(tr_d_val)

        st.markdown(
            f"""
            <div class="enterprise-card">
                <div class="card-header-flex">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="card-icon-box" style="background: #F0FDF4; color: #16A34A;">🔵</div>
                        <span class="metric-title">Transformer</span>
                    </div>
                    {badge}
                </div>
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Proximity Distance</div>
                <div class="metric-value-box">{tr_dist}</div>
                <div class="card-divider"></div>
                <div class="meta-row"><span class="meta-key">Voltage Capacity</span><span class="meta-val">{tr_volt}</span></div>
                <div class="meta-row"><span class="meta-key">Operator</span><span class="meta-val" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{tr_op}">{tr_op}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        land_value = land.get("land_value_eur_m2")
        municipality = land.get("municipality") or "--"
        district = land.get("district")

        if not district or str(district).lower() == "nan":
            district = "--"
        value = f"€ {land_value:,.0f} / m²" if land_value else "--"

        st.markdown(
            f"""
            <div class="enterprise-card">
                <div class="card-header-flex">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="card-icon-box" style="background: #FAF5FF; color: #7E22CE;">💶</div>
                        <span class="metric-title">Land Intelligence</span>
                    </div>
                    <span style="font-size: 10px; font-weight: 600; color: #7E22CE; background: #FAF5FF; padding: 3px 8px; border-radius: 6px; border: 1px solid #E9D5FF;">BORIS NRW</span>
                </div>
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Land Value</div>
                <div class="metric-value-box" style="font-size: 20px;">{value}</div>
                <div class="card-divider"></div>
                <div class="meta-row"><span class="meta-key">Municipality</span><span class="meta-val" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{municipality}">{municipality}</span></div>
                <div class="meta-row"><span class="meta-key">District</span><span class="meta-val" style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{district}">{district}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

#     # ---------------------------------------------------------
#     # SITE INTELLIGENCE SCORE
#     # ---------------------------------------------------------
#     # ---------------------------------------------------------
#     # SITE INTELLIGENCE SCORE
#     # ---------------------------------------------------------
#     st.html(
#         """
#          <div class="enterprise-card" style="
#         display:flex;
#         justify-content:space-between;
#         align-items:center;
#         padding:20px 24px;
#         margin-bottom:14px;
#     ">

#         <div>

#             <div style="
#                 font-size:14px;
#                 font-weight:600;
#                 color:#2563EB;
#                 text-transform:uppercase;
#                 letter-spacing:.8px;
#                 margin-bottom:6px;
#             ">
#                 Site Intelligence Score
#             </div>

#             <div style="
#                 font-size:28px;
#                 font-weight:700;
#                 color:#0F172A;
#                 margin-bottom:8px;
#             ">
#                 Infrastructure Suitability Assessment
#             </div>

#             <div style="
#                 font-size:14px;
#                 color:#64748B;
#                 max-width:720px;
#                 line-height:1.6;
#             ">
#                 The overall site score is calculated using proximity to high-voltage infrastructure,
#                 renewable energy availability, land valuation, transmission accessibility,
#                 and future expansion potential to identify the most suitable investment locations.
#             </div>

#         </div>

#         <div style="text-align:center;">

#             <div style="
#                 font-size:42px;
#                 font-weight:800;
#                 color:#CBD5E1;
#                 line-height:1;
#             ">
#                 --
#             </div>

#             <div style="
#                 font-size:13px;
#                 color:#94A3B8;
#                 margin-top:6px;
#             ">
#                 Awaiting Analysis
#             </div>

#         </div>

#     </div>
# """
#     )