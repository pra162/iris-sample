import streamlit as st


def render_kpis(summary: dict):

    cols = st.columns(6, gap="medium")

    with cols[0]:
        metric_card(
            "🏢",
            "Data Centers",
            f"{summary['facilities']:,}",
            "Active Facilities",
            format_trend(summary.get("facilities_trend", 0)),
            get_trend_type(summary.get("facilities_trend", 0)),
        )

    with cols[1]:
        metric_card(
            "🔌",
            "Power Infrastructure",
            f"{summary['power_infrastructure']:,}",
            "Substations / Lines",
            format_trend(summary.get("power_trend", 0)),
            get_trend_type(summary.get("power_trend", 0)),
        )

    with cols[2]:
        metric_card(
            "⚡",
            "Energy Assets",
            f"{summary['energy_assets']:,}",
            "Generation / Consumption",
            format_trend(summary.get("energy_trend", 0)),
            get_trend_type(summary.get("energy_trend", 0)),
        )

    with cols[3]:
        metric_card(
            "💶",
            "Avg Land Value",
            f"€{summary['average_land_value']:,.2f}/m²",
            "NRW Average",
            format_trend(summary.get("land_trend", 0)),
            get_trend_type(summary.get("land_trend", 0)),
        )

    with cols[4]:
        metric_card(
            "📰",
            "News Signals",
            f"{summary['news_signals']:,}",
            "Recent Events",
            format_trend(summary.get("news_trend", 0)),
            get_trend_type(summary.get("news_trend", 0)),
        )

    with cols[5]:
        metric_card(
            "🏆",
            "Avg Site Score",
            f"{summary['average_site_score']}",
            "Out of 100",
            format_trend(summary.get("site_score_trend", 0)),
            get_trend_type(summary.get("site_score_trend", 0)),
        )


def format_trend(value):

    if value > 0:
        return f"+{value}%"

    if value < 0:
        return f"{value}%"

    return "0%"


def get_trend_type(value):

    if value > 0:
        return "positive"

    if value < 0:
        return "negative"

    return "neutral"

def metric_card(
    icon: str,
    title: str,
    value: str,
    subtitle: str,
    trend: str,
    trend_type: str = "positive",
):
    if trend_type == "positive":
        trend_bg = "#DCFCE7"
        trend_color = "#15803D"
    elif trend_type == "negative":
        trend_bg = "#FEE2E2"
        trend_color = "#B91C1C"
    else:
        trend_bg = "#F1F5F9"
        trend_color = "#475569"

    html = f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div style="width: 36px; height: 36px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px;">
                {icon}
            </div>
            <div style="background: {trend_bg}; color: {trend_color}; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; display: inline-flex; align-items: center; gap: 2px;">
                {trend}
            </div>
        </div>
        <div>
            <div style="font-size: 11px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">{title}</div>
            <div style="font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 2px;">{value}</div>
            <div style="font-size: 11px; font-weight: 500; color: #94A3B8;">{subtitle}</div>
        </div>
    </div>
    """
    st.html(html)        