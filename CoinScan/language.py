# -*- coding: utf-8 -*-

# Dictionary containing translations for supported languages (German and English)
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
        "file": "Datei",
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
        "file": "File",
    },
}


def switch_language(lang, widgets, current_size):
    """
    Update the UI widgets to use the selected language.

    Args:
        lang (str): Language code ('de' or 'en').
        widgets (dict): Dictionary of Tkinter widgets to update.
        current_size (tuple): Current webcam resolution, used to set the size button text.
    """
    strings = LANGUAGES[lang]

    # Update main title
    widgets["title"].config(text=strings["title"])
    # Update scan button text
    widgets["scan_button"].config(text=strings["scan"])
    # Update total label text
    widgets["total_label"].config(text=strings["total"])
    # Update size button text depending on current resolution
    widgets["size_button"].config(
        text=(
            strings["size_plus"]
            if current_size == (320, 240)
            else strings["size_minus"]
        )
    )

    # Defensive: Update menu entries if present
    if "file_menu" in widgets:
        menu = widgets["file_menu"]
        idx = widgets.get("file_menu_exit_index", 0)
        end_idx = menu.index("end")
        if end_idx is not None and idx <= end_idx:
            try:
                menu.entryconfig(idx, label=strings["exit"])
            except Exception as e:
                print("Menu entry update failed:", e)
    if "menu_bar" in widgets:
        bar = widgets["menu_bar"]
        idx = widgets.get("file_menu_cascade_index", 0)
        end_idx = bar.index("end")
        if end_idx is not None and idx <= end_idx:
            try:
                bar.entryconfig(idx, label=strings.get("file", "File"))
            except Exception as e:
                print("Menu bar update failed:", e)