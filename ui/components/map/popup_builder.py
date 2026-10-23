from ui.components.map.map_styles import POPUP_FONT

def build_facility_popup(facility: dict) -> str:

    return f"""
<div style="
font-family:{POPUP_FONT};
width:260px;
background:white;
border-radius:14px;
overflow:hidden;
box-shadow:0 8px 30px rgba(0,0,0,.15);
">

<div style="
background:#16a34a;
padding:14px;
color:white;
">

<div style="font-size:16px;font-weight:700;">
🏢 {facility["name"]}
</div>

<div style="font-size:13px;opacity:.95;">
{facility["company"]}
</div>

</div>

<div style="padding:14px;">

<table style="width:100%;font-size:13px;border-collapse:collapse;">

<tr>
<td style="color:#64748b;">📍 City</td>
<td style="text-align:right;">
{facility["city"]}
</td>
</tr>

<tr>
<td style="padding-top:8px;color:#64748b;">
🌍 Country
</td>

<td style="padding-top:8px;text-align:right;">
{facility["country"]}
</td>

</tr>

</table>

<div style="
margin-top:16px;
padding:10px;
background:#ecfdf5;
border-left:5px solid #16a34a;
border-radius:8px;
font-size:12px;
font-weight:600;
">

✔ Operational Data Center

</div>

</div>

</div>
"""

def build_substation_popup(station: dict) -> str:

    return f"""
<div style="font-family:{POPUP_FONT};width:260px;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.15);">

<div style="background:#2563EB;padding:14px;color:white;">

<div style="font-size:16px;font-weight:700;">
⚡ {station["name"] or "Unnamed Substation"}
</div>

<div style="font-size:13px;opacity:.9;">
{station["operator"] or "-"}
</div>

</div>

<div style="padding:14px;">

<b>Voltage</b><br>
{station["voltage"] or "-"}<br><br>

<b>OSM ID</b><br>
{station["osm_id"]}

</div>

</div>
"""

def build_transformer_popup(transformer: dict) -> str:

    return f"""
<div style="font-family:{POPUP_FONT};width:260px;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.15);">

<div style="background:#9333EA;padding:14px;color:white;">

<div style="font-size:16px;font-weight:700;">
🔌 {transformer["name"] or "Transformer"}
</div>

<div style="font-size:13px;">
{transformer["operator"] or "-"}
</div>

</div>

<div style="padding:14px;">

<b>Voltage</b><br>
{transformer["voltage"] or "-"}<br><br>

<b>OSM ID</b><br>
{transformer["osm_id"]}

</div>

</div>
"""

def build_energy_popup(asset: dict) -> str:

    return f"""
<div style="font-family:{POPUP_FONT};width:260px;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.15);">

<div style="background:#EAB308;padding:14px;color:white;">

<div style="font-size:16px;font-weight:700;">
☀ {asset["name"]}
</div>

<div style="font-size:13px;">
{asset["energy_type"]}
</div>

</div>

<div style="padding:14px;">

<b>Operator</b><br>
{asset["operator"]}<br><br>

<b>Power</b><br>
{asset["gross_power_kw"]:,.0f} kW

</div>

</div>
"""