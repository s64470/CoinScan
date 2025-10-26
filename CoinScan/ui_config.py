# -*- coding: utf-8 -*-
# ui_config.py

# Font settings for different UI elements
UI_FONT = ("Verdana", 11)                   # Standard font for general UI elements
TITLE_FONT = ("Verdana", 14, "bold")        # Larger, bold font for titles
MONO_FONT = ("Consolas", 10)                # Monospaced font for listboxes or code-like text

# Button style configuration for consistent appearance
BUTTON_STYLE = {
    "font": UI_FONT,                        # Use the standard UI font
    "bg": "#3498db",                        # Button background color (blue)
    "fg": "white",                          # Button text color
    "activebackground": "#2980b9",          # Background color when button is pressed or hovered
    "activeforeground": "white",            # Text color when button is pressed or hovered
    "relief": "raised",                     # Button border style
    "bd": 2,                                # Border width
    "padx": 10,                             # Horizontal padding inside button
    "pady": 5,                              # Vertical padding inside button
}


def on_enter(e):
    """
    Event handler for mouse entering a button.
    Changes the button background to the active color.
    """
    e.widget["background"] = "#2980b9"


def on_leave(e):
    """
    Event handler for mouse leaving a button.
    Restores the button background to the default color.
    """
    e.widget["background"] = "#3498db"