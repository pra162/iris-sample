"""
Shared map styles for the NRW Infrastructure Dashboard.

This module centralizes all colors and visual styling
used across the map layers.
"""

# ==========================================================
# Base Map
# ==========================================================

MAP_CENTER = [51.433, 7.661]
MAP_ZOOM = 8
MAP_TILES = "CartoDB Voyager"

# ==========================================================
# Facilities
# ==========================================================

FACILITY_COLOR = "#16A34A"
FACILITY_BORDER = "#FFFFFF"
FACILITY_RADIUS = 7

# ==========================================================
# Transformers
# ==========================================================

TRANSFORMER_COLOR = "#2563EB"
TRANSFORMER_BORDER = "#FFFFFF"
TRANSFORMER_RADIUS = 5

# ==========================================================
# Energy Assets
# ==========================================================

ENERGY_COLOR = "#9333EA"
ENERGY_BORDER = "#FFFFFF"
ENERGY_RADIUS = 6

# ==========================================================
# High Voltage Substations
# ==========================================================

SUBSTATION_110KV_COLOR = "#EAB308"
SUBSTATION_220KV_COLOR = "#EA580C"
SUBSTATION_380KV_COLOR = "#991B1B"

SUBSTATION_110KV_RADIUS = 7
SUBSTATION_220KV_RADIUS = 8
SUBSTATION_380KV_RADIUS = 9

SUBSTATION_BORDER = "#FFFFFF"

# ==========================================================
# Transmission Lines
# ==========================================================

LINE_110KV_COLOR = "#EAB308"
LINE_220KV_COLOR = "#EA580C"
LINE_380KV_COLOR = "#DC2626"

LINE_110KV_WEIGHT = 2
LINE_220KV_WEIGHT = 3
LINE_380KV_WEIGHT = 4

LINE_OPACITY = 0.8

# ==========================================================
# Marker Styling
# ==========================================================

MARKER_BORDER_WEIGHT = 1.5
MARKER_FILL_OPACITY = 1.0

# ==========================================================
# Popup Styling
# ==========================================================

POPUP_WIDTH = 260
SMALL_POPUP_WIDTH = 220

POPUP_FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"