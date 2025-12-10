"""
Configuration and constants for the Neubond Clinician Dashboard.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON = os.getenv("SUPABASE_SECRET_KEY")

# Dev Impersonation (for testing clinicians without passwords)
ENV = os.getenv("ENV", "prod")
DEV_IMPERSONATE_USER_IDS = os.getenv("DEV_IMPERSONATE_USER_IDS", "").split(",") if ENV == "dev" else []

# App Configuration
APP_TITLE = "Neubond Clinician Dashboard"
PAGE_LAYOUT = "wide"

# EMG Plot Configuration
EMG_CHANNEL_OFFSET = 2000  # Vertical offset between channels
EMG_FIGURE_SIZE = (12, 4)
EMG_LINE_WIDTH = 0.8
EMG_GAP_DETECTION_FACTOR = 5.0  # Threshold multiplier for gap detection

# Phase Colors for EMG Plotting
PHASE_COLORS = {
    "attempt": "#ff6b6b",
    "rest": "#6ba4ff"
}

# Session Plot Configuration
SESSION_CHART_HEIGHT_BARS = 150
SESSION_CHART_HEIGHT_SCATTER = 200

# Export Configuration
EXPORT_FORMATS = {
    "csv": "text/csv",
    "mat": "application/octet-stream"
}

# Timestamp Display Format
TIMESTAMP_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_DISPLAY_FORMAT_SHORT = "%m/%d %H:%M"

# Clinical Analysis Placeholders (for future features)
# TODO: Add configuration for:
# - Day of week analysis colors/labels
# - Time of day binning (morning/afternoon/evening)
# - EMG amplitude thresholds
# - Co-contraction detection parameters
# - Trend analysis window sizes
