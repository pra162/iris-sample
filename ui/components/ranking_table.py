import streamlit as st


def render_ranking_table(rankings):

    st.write(rankings)
    return
    data = []

    for index, site in enumerate(rankings):

        data.append(
            {
                "Rank": index + 1,
                "Facility Name": (
                    site.get("facility_name")
                    or site.get("name")
                    or "-"
                ),
                "City": site.get("city", "-"),
                "Operator": site.get("company", "-"),
                "Site Score": round(
                    site.get("overall_score", 0),
                    1,
                ),
                "Cap. (MW)": site.get(
                    "capacity_mw",
                    "-",
                ),
                "Dist. to Substation": (
                    f"{round(site.get('substation_distance_m', 0))} m"
                    if site.get("substation_distance_m")
                    else "-"
                ),
                "Land Value (€/m²)": (
                    f"€{round(site.get('land_value', 0), 2)}"
                    if site.get("land_value")
                    else "-"
                ),
            }
        )

    rows_html = ""

    for i, row in enumerate(data):

        bg_color = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"

        rank_display = (
            f'<span style="display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;background:#0F172A;color:white;border-radius:3px;font-size:9px;font-weight:700;">{row["Rank"]}</span>'
            if row["Rank"] <= 3
            else f'<span style="color:#64748B;font-weight:600;padding-left:2px;">{row["Rank"]}</span>'
        )

        score_badge = (
            f'<span style="background:#ECFDF5;color:#059669;padding:2px 5px;border-radius:4px;font-weight:700;border:1px solid #A7F3D0;font-size:10px;">{row["Site Score"]}</span>'
        )

        rows_html += f"""
        <tr style="background:{bg_color};">
            <td>{rank_display}</td>
            <td>{row["Facility Name"]}</td>
            <td>{row["City"]}</td>
            <td>{row["Operator"]}</td>
            <td>{score_badge}</td>
            <td>{row["Cap. (MW)"]}</td>
            <td>{row["Dist. to Substation"]}</td>
            <td>{row["Land Value (€/m²)"]}</td>
        </tr>
        """

    card_html = f"""
    ...
    {rows_html}
    ...
    """

    st.html(card_html)