def get_voltage_style(voltage: str | None):

    voltage = voltage or ""

    if "380000" in voltage:
        return {
            "substation_color": "#991B1B",   # Dark Red
            "line_color": "#991B1B",
            "transformer_radius": 8,
            "substation_radius": 9,
            "line_weight": 4,
        }

    if "220000" in voltage:
        return {
            "substation_color": "#EA580C",   # Orange
            "line_color": "#EA580C",
            "transformer_radius": 7,
            "substation_radius": 8,
            "line_weight": 3,
        }

    if "150000" in voltage:
        return {
            "substation_color": "#F59E0B",   # Amber
            "line_color": "#F59E0B",
            "transformer_radius": 6,
            "substation_radius": 7,
            "line_weight": 2.5,
        }

    if "110000" in voltage:
        return {
            "substation_color": "#2563EB",   # Blue
            "line_color": "#2563EB",
            "transformer_radius": 5,
            "substation_radius": 6,
            "line_weight": 2,
        }

    return {
        "substation_color": "#64748B",
        "line_color": "#64748B",
        "transformer_radius": 5,
        "substation_radius": 5,
        "line_weight": 1,
    }