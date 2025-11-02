# ui_config.py
# Central configuration for UI appearance and behaviour in CoinScan

LOGO_WIDTH = 50  # Set your desired logo/sidebar width here

# Colour palette for the app
COLORS = {
    "background": "#f4f6f8",      # Main window background
    "panel_bg": "white",          # Panel backgrounds
    "sidebar_bg": "#2c3e50",      # Sidebar background
    "sidebar_fg": "white",        # Sidebar foreground (text/icons)
    "topbar_bg": "#f8f8f8",       # Top bar background
    "button_bg": "#3498db",       # Button background
    "button_fg": "white",         # Button foreground (text)
    "button_active_bg": "#2980b9",# Button background when active
    "button_active_fg": "white",  # Button foreground when active
    "results_fg": "#3498db",      # Results text colour
    "contrast_bg": "#000000",     # High-contrast background
    "contrast_fg": "#FFFF00",     # High-contrast foreground
    "contrast_panel_bg": "#222222", # High-contrast panel background
    "contrast_sidebar_bg": "#000000", # High-contrast sidebar background
    "contrast_sidebar_fg": "#FFFF00", # High-contrast sidebar foreground
}

# Font settings for various UI elements
FONTS = {
    "title": ("Segoe UI", 18, "bold"),      # Main title
    "sidebar": ("Segoe UI", 16),            # Sidebar icons
    "version": ("Segoe UI", 10, "bold"),    # Version label
    "button": ("Segoe UI", 14, "bold"),     # Main buttons
    "results": ("Segoe UI", 14, "bold"),    # Results label
    "total": ("Segoe UI", 16, "bold"),      # Total label
    "listbox": ("Segoe UI", 12),            # Listbox font
    "about_title": ("Segoe UI", 16, "bold"),# About dialog title
    "about_text": ("Segoe UI", 11),         # About dialog text
    "about_button": ("Segoe UI", 11),       # About dialog button
    "size_button": ("Segoe UI", 12),        # Webcam size buttons
    "footer": ("Segoe UI", 8),              # Footer copyright (smaller font)
}

# File paths for icons (flags)
ICON_PATHS = {
    "flag_de": "icon/flag_DE.png",  # German flag
    "flag_en": "icon/flag_UK.png",  # UK flag
}

# Standard sizes for UI elements
SIZES = {
    "window": (1200, 700),         # Main window size
    "webcam_small": (480, 360),    # Small webcam resolution
    "webcam_large": (800, 600),    # Large webcam resolution
    "flag": (24, 24),              # Flag icon size
    "sidebar_width": LOGO_WIDTH,   # Sidebar width matches logo width
    "logo_width": LOGO_WIDTH,      # Logo width
    "footer_height": 30,           # Footer height
}

# Unicode icons for sidebar buttons
SIDEBAR_ICONS = [
    "\U0001f3e0",      # Home
    "\u2699\ufe0f",    # Settings
    "\u2753",          # About / Help
    "\u23fb",          # Exit (⏻)
]

# Icons for contrast mode toggle
CONTRAST_ICONS = {
    "normal": "\U0001f313",        # Crescent moon (normal mode)
    "contrast": "\u2600\ufe0f",    # Sun (high-contrast mode)
}