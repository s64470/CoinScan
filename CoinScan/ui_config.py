# -*- coding: utf-8 -*-
# ui_config.py

UI_FONT = ("Verdana", 11)
TITLE_FONT = ("Verdana", 14, "bold")
MONO_FONT = ("Consolas", 10)

BUTTON_STYLE = {
    "font": UI_FONT,
    "bg": "#3498db",
    "fg": "white",
    "activebackground": "#2980b9",
    "activeforeground": "white",
    "relief": "raised",
    "bd": 2,
    "padx": 10,
    "pady": 5,
}


def on_enter(e):
    e.widget["background"] = "#2980b9"


def on_leave(e):
    e.widget["background"] = "#3498db"