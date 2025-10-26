# -*- coding: utf-8 -*-
# This file manages all language-dependent UI strings and provides a function
# to update the application's UI elements when the language is changed.

# LANGUAGES dictionary holds all UI text for both German ("de") and English ("en").
LANGUAGES = {
    "de": {
        "title": "LIVE SCAN",  # Main window title
        "scan": "🔍 Münzen scannen",  # Scan button text
        "exit": "❌ Programm Beenden",  # Exit menu/button text
        "total": "GESAMT: 0,00 €",  # Total label text
        "size_plus": "🔎 +",  # Webcam size increase button
        "size_minus": "🔎 -",  # Webcam size decrease button
        "exit_dialog_title": "Beenden",  # Exit dialog title
        "exit_dialog_text": "Möchten Sie das Programm wirklich beenden?",  # Exit dialog message
        "file": "Datei",  # File menu label
        "help": "Hilfe",  # Help menu label
        "help_dialog_title": "Hilfe",  # Help dialog title
        "help_dialog_text": (
            "Willkommen bei MünzScan!\n\n"
            "- Klicken Sie auf 'Münzen scannen', um den Scan zu starten.\n"
            "- Mit dem blauen Button können Sie die Webcam-Auflösung ändern.\n"
            "- Über die Flaggen wechseln Sie die Sprache.\n"
            "- Das Programm erkennt Münzen und zeigt die Summe an.\n\n"
            "Bei Problemen wenden Sie sich bitte an den Entwickler."
        ),  # Help dialog message
    },
    "en": {
        "title": "LIVE SCAN",  # Main window title
        "scan": "🔍 Scan Coins",  # Scan button text
        "exit": "❌ Exit",  # Exit menu/button text
        "total": "TOTAL: €0.00",  # Total label text
        "size_plus": "🔎 +",  # Webcam size increase button
        "size_minus": "🔎 -",  # Webcam size decrease button
        "exit_dialog_title": "Exit",  # Exit dialog title
        "exit_dialog_text": "Are you sure you want to exit?",  # Exit dialog message
        "file": "File",  # File menu label
        "help": "Help",  # Help menu label
        "help_dialog_title": "Help",  # Help dialog title
        "help_dialog_text": (
            "Welcome to CoinScan!\n\n"
            "- Click 'Scan Coins' to start scanning.\n"
            "- Use the blue button to change webcam resolution.\n"
            "- Switch language using the flags.\n"
            "- The program recognizes coins and shows the total.\n\n"
            "For issues, please contact the developer."
        ),  # Help dialog message
    },
}

def switch_language(lang, widgets, current_size):
    """
    Update all UI elements to the selected language.

    Args:
        lang (str): Language code ("de" or "en").
        widgets (dict): Dictionary containing references to all UI widgets.
        current_size (tuple): Current webcam resolution.
    """
    strings = LANGUAGES.get(lang, LANGUAGES["en"])  # Fallback to English if lang not found

    # Update main title label
    if "title" in widgets:
        widgets["title"].config(text=strings["title"])

    # Update scan button text
    if "scan_button" in widgets:
        widgets["scan_button"].config(text=strings["scan"])

    # Update total label text
    if "total_label" in widgets:
        widgets["total_label"].config(text=strings["total"])

    # Update webcam size button text depending on current resolution
    if "size_button" in widgets:
        widgets["size_button"].config(
            text=strings["size_plus"] if current_size == (320, 240) else strings["size_minus"]
        )

    # Update File menu entry (Exit)
    if "file_menu" in widgets:
        menu = widgets["file_menu"]
        idx = widgets.get("file_menu_exit_index", 0)
        try:
            menu.entryconfig(idx, label=strings["exit"])
        except Exception as e:
            print("Menu entry update failed:", e)

    # Update Help menu entry
    if "help_menu" in widgets:
        help_menu = widgets["help_menu"]
        idx = widgets.get("help_menu_index", 0)
        try:
            help_menu.entryconfig(idx, label=strings["help"], image=widgets.get("help_icon"), compound="left")
        except Exception as e:
            print("Help menu entry update failed:", e)

    # Update menu bar labels ("File" and "Help") safely
    if "menu_bar" in widgets:
        menu_bar = widgets["menu_bar"]

        # Clear all existing menu entries to avoid duplicates
        try:
            menu_bar.delete(0, "end")
        except Exception as e:
            print("Menu bar clear failed:", e)

        # Re-add cascades with updated labels
        try:
            menu_bar.add_cascade(label=strings["file"], menu=widgets["file_menu"])
            menu_bar.add_cascade(label=strings["help"], menu=widgets["help_menu"])
        except Exception as e:
            print("Menu bar add_cascade failed:", e)