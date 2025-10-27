# -*- coding: utf-8 -*-
# UI configuration: font parameters, button style parameters, and hover effects

# Font parameters (not Font objects!)
UI_FONT_PARAMS = {"family": "Verdana", "size": 11}
TITLE_FONT_PARAMS = {"family": "Verdana", "size": 14, "weight": "bold"}
MONO_FONT_PARAMS = {"family": "Consolas", "size": 10}

# Button style parameters (no font yet)
BUTTON_STYLE_PARAMS = {
    "bg": "#3498db",
    "fg": "white",
    "activebackground": "#2980b9",
    "activeforeground": "white",
    "relief": "raised",
    "bd": 2,
    "padx": 10,
    "pady": 5,
}


# Button hover effects (to be used in main file)
def on_enter(e):
    """Change button background color on hover."""
    e.widget["background"] = BUTTON_STYLE_PARAMS["activebackground"]


def on_leave(e):
    """Reset button background color when not hovered."""
    e.widget["background"] = BUTTON_STYLE_PARAMS["bg"]