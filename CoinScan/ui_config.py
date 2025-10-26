# -*- coding: utf-8 -*-
# This file defines the UI style and button hover behavior for the application.

# Font settings for different UI elements
UI_FONT = ("Verdana", 11)           # Standard font for most UI elements
TITLE_FONT = ("Verdana", 14, "bold")# Font for main titles
MONO_FONT = ("Consolas", 10)        # Monospaced font for lists or code-like displays

# Button style settings (used for all main buttons)
BUTTON_STYLE = {
    "font": UI_FONT,                # Button font
    "bg": "#3498db",                # Button background color (blue)
    "fg": "white",                  # Button text color
    "activebackground": "#2980b9",  # Background color when button is pressed or hovered
    "activeforeground": "white",    # Text color when button is pressed or hovered
    "relief": "raised",             # Button border style
    "bd": 2,                        # Border width
    "padx": 10,                     # Horizontal padding inside button
    "pady": 5,                      # Vertical padding inside button
}

def on_enter(e):
    """
    Change button background color when the mouse pointer enters the button.
    This provides a visual hover effect.
    """
    e.widget["background"] = "#2980b9"

def on_leave(e):
    """
    Reset button background color when the mouse pointer leaves the button.
    """
    e.widget["background"] = "#3498db"