"""
PyDeck Map Builder

Responsible for creating the complete Deck object.

No business logic.
No database calls.
No Streamlit.
"""

import pydeck as pdk

from .map_styles import (
    INITIAL_VIEW,
    MAP_STYLE,
)


def build_map(
    layers: list[pdk.Layer],
) -> pdk.Deck:
    """
    Builds the complete PyDeck map.
    """

    return pdk.Deck(
        layers=layers,

        initial_view_state=INITIAL_VIEW,

        map_style=MAP_STYLE,

        tooltip={
        "html": """
        <div style="
            padding:12px;
            font-family:Inter;
            min-width:220px;
        ">

            <div style="
                font-size:15px;
                font-weight:700;
                margin-bottom:8px;
            ">
                {name}
            </div>

            <div><b>🏢 Company:</b> {company}</div>
            <div><b>📍 City:</b> {city}</div>
            <div><b>⚡ Voltage:</b> {voltage}</div>
            <div><b>🏭 Operator:</b> {operator}</div>

        </div>
        """,
        "style": {
            "backgroundColor": "#111827",
            "color": "white",
            "borderRadius": "12px",
        },
    }
    )