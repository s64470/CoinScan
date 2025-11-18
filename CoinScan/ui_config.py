# UI configuration constants for CoinScan application.
# Contains colors, fonts, sizes and icon paths used by the UI.

from pathlib import Path


# Default width used for logos and sidebar icons
# Increased to make `logo-prosegur.png` larger in the top bar and other UI locations.
LOGO_WIDTH = 50


# Color palette used throughout the UI (hex color strings)
COLORS = {
    "background": "#FFD100",
    "panel_bg": "#FFFFFF",
    "sidebar_bg": "#2c3e50",
    "sidebar_fg": "#FFFFFF",
    "topbar_bg": "#F5C800",
    "button_bg": "#3498db",
    "button_fg": "#FFFFFF",
    "button_active_bg": "#2980b9",
    "button_active_fg": "#FFFFFF",
    "results_fg": "#3498db",
    "footer_bg": "#FFD100",
    "footer_fg": "#000000",
    "listbox_bg": "#FFE680",
    "contrast_bg": "#000000",
    "contrast_fg": "#FFFF00",
    "contrast_panel_bg": "#000000",
    "contrast_sidebar_bg": "#000000",
    "contrast_sidebar_fg": "#FFFF00",
    "primary_btn_bg": "#0057B7",
    "primary_btn_hover": "#004C9F",
    "font_btn_inc_bg": "#2ecc71",
    "font_btn_inc_hover": "#27ae60",
    "font_btn_dec_bg": "#e67e22",
    "font_btn_dec_hover": "#d35400",
    "font_btn_disabled_bg": "#000000",
    "font_btn_disabled_fg": "#FFFF00",
}


# Font definitions used in the UI: (family, size, [style])
FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "sidebar": ("Segoe UI", 16),
    "version": ("Segoe UI", 10, "bold"),
    "button": ("Segoe UI", 14, "bold"),
    "results": ("Segoe UI", 14, "bold"),
    "total": ("Segoe UI", 16, "bold"),
    "listbox": ("Segoe UI", 12),
    "about_title": ("Segoe UI", 16, "bold"),
    "about_text": ("Segoe UI", 11),
    "about_button": ("Segoe UI", 11),
    "size_button": ("Segoe UI", 12),
    "footer": ("Segoe UI", 8),
}


# Directory containing icon image files (relative to this file)
ICON_DIR = Path(__file__).parent / "icon"


# Absolute paths (strings) to specific icon files used by the app
ICON_PATHS = {
    "flag_de": str((ICON_DIR / "flag_DE.png").resolve()),
    "flag_en": str((ICON_DIR / "flag_UK.png").resolve()),
    "prosegur": str((ICON_DIR / "prosegur.png").resolve()),
    "prosegur_globe": str((ICON_DIR / "prosegur_globe.png").resolve()),
}


# Mapping of logical logos to their high-contrast image paths. UI can use this when contrast mode is enabled.
HIGH_CONTRAST_LOGOS = {
    "prosegur": ICON_PATHS["prosegur_globe"],
}


# Standard sizes for windows, webcams and UI elements
SIZES = {
    "window": (1600, 950),
    "webcam_small": (480, 360),
    "webcam_large": (800, 600),
    "webcam_xl": (1280, 960),
    "flag": (24, 24),
    "sidebar_width": LOGO_WIDTH,
    "logo_width": LOGO_WIDTH,
    "footer_height": 30,
}


# Unicode icons displayed in the sidebar (simple glyphs)
SIDEBAR_ICONS = [
    "\U0001f3e0",  # home
    "\u2699\ufe0f",  # gear
    "\u2753",  # question mark
    "\u23fb",  # power / standby
]


# Icons used to indicate normal vs contrast mode
CONTRAST_ICONS = {
    "normal": "\U0001f313",
    "contrast": "\u2600\ufe0f",
}


# Check if required icon files exist and warn at import time if missing
_missing_icons = [k for k, p in ICON_PATHS.items() if not Path(p).exists()]
if _missing_icons:
    # These icon files are optional. Log at DEBUG level instead of raising a
    # RuntimeWarning so import-time output stays clean in normal runs. Use a
    # logger so developers can enable debug logging when needed.
    import logging

    logging.getLogger(__name__).debug(
        "Optional icon files missing: %s", ", ".join(_missing_icons)
    )