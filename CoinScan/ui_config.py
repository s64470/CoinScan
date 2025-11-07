# ui_config.py
# Central configuration for UI appearance and behaviour in CoinScan

"""
ui_config.py

Purpose:
- Central place to define UI constants used across the application.
- Keeps presentation settings (sizes, fonts, colours, icons) decoupled from UI logic.

Notes:
- Values here are plain Python constants (ints, tuples, dicts). Import them where needed:
    from ui_config import COLORS, FONTS, SIZES, ICON_PATHS, SIDEBAR_ICONS, CONTRAST_ICONS
- Update these values to change the app theme or to add accessibility options (e.g. high-contrast).
"""

# Width used for the logo and sidebar. Adjust to change sidebar size consistently.
LOGO_WIDTH = 50  # pixels

# Colour palette for the app.
# Keys represent logical UI areas; values are color strings (hex or named colours supported by the toolkit).
COLORS = {
    # Updated to Prosegur corporate yellow (approximate hex: #FFD100)
    # Source: Public brand colour references (Pantone 109C / Prosegur Yellow)
    "background": "#FFD100",  # Main window background colour (Prosegur Yellow)
    "panel_bg": "white",  # Panel / card background colour
    "sidebar_bg": "#2c3e50",  # Sidebar background (dark blue/gray)
    "sidebar_fg": "white",  # Sidebar foreground (text/icons)
    "topbar_bg": "#FFD100",  # Match top bar with corporate yellow for consistency
    "button_bg": "#3498db",  # Primary button background (blue)
    "button_fg": "white",  # Primary button text colour
    "button_active_bg": "#2980b9",  # Button background when hovered/active
    "button_active_fg": "white",  # Button text when active
    "results_fg": "#3498db",  # Colour for result text / highlights
    # High-contrast mode colours (for accessibility).
    # Intent: map greys/darks to pure black and important text to a bright colour.
    "contrast_bg": "#000000",  # High-contrast app background (BLACK)
    "contrast_fg": "#FFFF00",  # High-contrast foreground (YELLOW)
    "contrast_panel_bg": "#000000",  # High-contrast panel background (BLACK)
    "contrast_sidebar_bg": "#000000",  # High-contrast sidebar background (BLACK)
    "contrast_sidebar_fg": "#FFFF00",  # High-contrast sidebar foreground (YELLOW)
}

# Font settings for various UI elements.
# Each entry is a tuple typically in the form (family, size, style?).
# The exact tuple interpretation depends on the UI toolkit in use (e.g., Tkinter expects this shape).
FONTS = {
    "title": ("Segoe UI", 18, "bold"),  # Main application title
    "sidebar": ("Segoe UI", 16),  # Sidebar labels / icons
    "version": ("Segoe UI", 10, "bold"),  # Small version label text
    "button": ("Segoe UI", 14, "bold"),  # Primary buttons
    "results": ("Segoe UI", 14, "bold"),  # Results text (e.g., identified coin)
    "total": ("Segoe UI", 16, "bold"),  # Total / summary label
    "listbox": ("Segoe UI", 12),  # Listbox items
    "about_title": ("Segoe UI", 16, "bold"),  # About dialog title
    "about_text": ("Segoe UI", 11),  # About dialog body text
    "about_button": ("Segoe UI", 11),  # About dialog button
    "size_button": ("Segoe UI", 12),  # Buttons to select webcam size
    "footer": ("Segoe UI", 8),  # Footer / copyright (small)
}

# File paths for icon assets (flag images here).
# Paths are relative to the project root; ensure files exist at these locations.
ICON_PATHS = {
    "flag_de": "icon/flag_DE.png",  # German flag image path
    "flag_en": "icon/flag_UK.png",  # English / UK flag image path
}

# Standard sizes used across the UI. All sizes are tuples in (width, height) where applicable.
SIZES = {
    # Make the window a bit larger so XL webcam fits alongside the results panel.
    "window": (1600, 950),  # Default main window size (width, height)
    "webcam_small": (480, 360),  # Small webcam capture/frame size (4:3)
    "webcam_large": (800, 600),  # Large webcam capture/frame size (4:3)
    "webcam_xl": (1280, 960),  # Extra large webcam capture/frame size (4:3)
    "flag": (24, 24),  # Flag icon display size (width, height)
    # Keep sidebar/logo widths in sync by reusing LOGO_WIDTH constant.
    "sidebar_width": LOGO_WIDTH,  # Sidebar width (pixels)
    "logo_width": LOGO_WIDTH,  # Logo width (pixels)
    "footer_height": 30,  # Footer bar height (pixels)
}

# Unicode icons used for sidebar buttons.
# These are simple text glyphs and avoid external assets for these common actions.
SIDEBAR_ICONS = [
    "\U0001f3e0",  # Home (house)
    "\u2699\ufe0f",  # Settings (gear)
    "\u2753",  # About / Help (question mark)
    "\u23fb",  # Exit / Power (power symbol: ⏻)
]

# Icons used for contrast mode toggle (text glyphs).
# Map a logical state name to a unicode symbol; used where an image isn't needed.
CONTRAST_ICONS = {
    "normal": "\U0001f313",  # Crescent moon (normal / dark mode icon)
    "contrast": "\u2600\ufe0f",  # Sun (high-contrast / bright mode icon)
}