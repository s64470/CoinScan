"""
UI configuration constants for the CoinScan application.

Contains colors, fonts, sizes and icon paths used by the UI.
This file provides typed constants and a small helper for retrieving icon paths.
"""

from pathlib import Path
from typing import Dict, Tuple

# Default width used for logos and sidebar icons.
LOGO_WIDTH: int = 50

# Color palette used throughout the UI (hex color strings).
COLORS: Dict[str, str] = {
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

# Font definitions used in the UI: (family, size, [style]).
FONTS: Dict[str, Tuple] = {
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

# Directory containing icon image files (relative to this file).
ICON_DIR: Path = Path(__file__).parent / "icon"

# Known icon filenames (keeps mapping clear and easy to extend).
_ICON_FILES: Dict[str, str] = {
    "flag_de": "flag_DE.png",
    "flag_en": "flag_UK.png",
    "prosegur": "prosegur.png",
    "prosegur_globe": "prosegur_globe.png",
}

# Absolute-ish paths (string) to specific icon files used by the app.
# Use resolve(strict=False) to avoid raising if files are not present at import time.
ICON_PATHS: Dict[str, str] = {
    key: str((ICON_DIR / filename).resolve(strict=False)) for key, filename in _ICON_FILES.items()
}

# Mapping of logical logos to their high-contrast image paths.
HIGH_CONTRAST_LOGOS: Dict[str, str] = {
    "prosegur": ICON_PATHS["prosegur_globe"],
}

# Standard sizes for windows, webcams and UI elements.
SIZES: Dict[str, Tuple[int, int] | int] = {
    "window": (1600, 950),
    "webcam_small": (480, 360),
    "webcam_large": (800, 600),
    "webcam_xl": (1280, 960),
    "flag": (24, 24),
    "sidebar_width": LOGO_WIDTH,
    "logo_width": LOGO_WIDTH,
    "footer_height": 30,
}

# Unicode icons displayed in the sidebar (simple glyphs).
SIDEBAR_ICONS: Tuple[str, ...] = (
    "\U0001f3e0",  # home
    "\u2699\ufe0f",  # gear
    "\u2753",  # question mark
    "\u23fb",  # power / standby
)

# Icons used to indicate normal vs contrast mode.
CONTRAST_ICONS: Dict[str, str] = {
    "normal": "\U0001f313",
    "contrast": "\u2600\ufe0f",
}


def icon_path(name: str) -> str:
    """
    Return the path string for a named icon. If the icon is unknown returns an empty string.
    Use this helper in UI code to avoid accessing ICON_PATHS directly.
    """
    return ICON_PATHS.get(name, "")


__all__ = [
    "LOGO_WIDTH",
    "COLORS",
    "FONTS",
    "ICON_DIR",
    "ICON_PATHS",
    "HIGH_CONTRAST_LOGOS",
    "SIZES",
    "SIDEBAR_ICONS",
    "CONTRAST_ICONS",
    "icon_path",
]