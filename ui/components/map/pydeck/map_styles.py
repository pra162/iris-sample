"""
PyDeck Map Styling

Centralized styling for the entire GIS platform.
"""

import pydeck as pdk


# ==========================================================
# Initial View
# ==========================================================

INITIAL_VIEW = pdk.ViewState(
    latitude=51.4332,
    longitude=7.6616,
    zoom=7,
    pitch=20,
    bearing=0,
)

# ==========================================================
# Map Theme
# ==========================================================

# MAP_STYLE = pdk.map_styles.LIGHT
MAP_STYLE = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
# Alternative styles:
#
# pdk.map_styles.LIGHT
# pdk.map_styles.DARK
# pdk.map_styles.ROAD
# pdk.map_styles.SATELLITE
#
# We'll make this configurable later.


# ==========================================================
# Colors
# ==========================================================

# FACILITY_COLOR = [37, 99, 235]      # Professional blue
FACILITY_COLOR = [30, 136, 229]
FACILITY_RADIUS = 2200

SUBSTATION_110KV = [255, 193, 7]
SUBSTATION_220KV = [255, 152, 0]
SUBSTATION_380KV = [244, 67, 54]

TRANSFORMER_COLOR = [124, 58, 237]

LINE_110KV = [59, 130, 246]
LINE_220KV = [245, 158, 11]
LINE_380KV = [220, 38, 38]

ENERGY_COLOR = [22,163,74]        # Green

# ==========================================================
# Radius (meters)
# ==========================================================

# FACILITY_RADIUS = 1200

SUBSTATION_RADIUS = 1400

TRANSFORMER_RADIUS = 1100

ENERGY_RADIUS = 800