# -*- coding: utf-8 -*-
# language.py

# Dictionary containing UI strings for supported languages (German and English)
LANGUAGES = {
    "de": {  # German translations
        "title": "LIVE SCAN",
        "scan": "🔍 Münzen scannen",
        "exit": "❌ Programm Beenden",
        "total": "GESAMT: 0,00 €",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
        "exit_dialog_title": "Beenden",
        "exit_dialog_text": "Möchten Sie das Programm wirklich beenden?",
    },
    "en": {  # English translations
        "title": "LIVE SCAN",
        "scan": "🔍 Scan Coins",
        "exit": "❌ Exit",
        "total": "TOTAL: €0.00",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
        "exit_dialog_title": "Exit",
        "exit_dialog_text": "Are you sure you want to exit?",
    },
}


def switch_language(lang, widgets, current_size):
    """
    Update the UI widget texts to match the selected language.

    Args:
        lang (str): Language code ('de' or 'en').
        widgets (dict): Dictionary of Tkinter widgets to update.
        current_size (tuple): Current webcam resolution, used to set size button text.
    """
    strings = LANGUAGES[lang]
    widgets["title"].config(text=strings["title"])
    widgets["scan_button"].config(text=strings["scan"])
    widgets["exit_button"].config(text=strings["exit"])
    widgets["total_label"].config(text=strings["total"])
    widgets["size_button"].config(
        text=(
            strings["size_plus"]
            if current_size == (320, 240)
            else strings["size_minus"]
        )
    )