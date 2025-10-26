# -*- coding: utf-8 -*-

# Font settings for various UI elements
UI_FONT = ("Verdana", 11)  # General UI font
TITLE_FONT = ("Verdana", 14, "bold")  # Font for titles/headings
MONO_FONT = ("Consolas", 10)  # Monospaced font for lists or code-like text

# Button style configuration for consistent appearance
BUTTON_STYLE = {
    "font": UI_FONT,                # Font for button text
    "bg": "#3498db",                # Default background color
    "fg": "white",                  # Default foreground/text color
    "activebackground": "#2980b9",  # Background color when button is pressed/hovered
    "activeforeground": "white",    # Text color when button is pressed/hovered
    "relief": "raised",             # Button border style
    "bd": 2,                        # Border width
    "padx": 10,                     # Horizontal padding inside button
    "pady": 5,                      # Vertical padding inside button
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
    Resets the button background to the default color.
    """
    e.widget["background"] = "#3498db"