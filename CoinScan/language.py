# -*- coding: utf-8 -*-
# Language management for the UI

LANGUAGES = {
    "de": {
        "title": "LIVE SCAN",
        "scan": "🔍 Münzen scannen",
        "exit": "❌ Programm Beenden",
        "total": "GESAMT: 0,00 €",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
        "exit_dialog_title": "Beenden",
        "exit_dialog_text": "Möchten Sie das Programm wirklich beenden?",
        "file": "Datei",
        "settings": "Einstellungen",
        "help": "Hilfe",
        "help_dialog_title": "Hilfe",
        "help_dialog_text": (
            "Willkommen bei MünzScan!\n\n"
            "- Klicken Sie auf 'Münzen scannen', um den Scan zu starten.\n"
            "- Mit dem blauen Button können Sie die Webcam-Auflösung ändern.\n"
            "- Über die Flaggen wechseln Sie die Sprache.\n"
            "- Das Programm erkennt Münzen und zeigt die Summe an.\n\n"
            "Bei Problemen wenden Sie sich bitte an den Entwickler."
        ),
        "about_title": "Über CoinScan",
        "about_text": (
            "CoinScan\n"
            "Version: 1.0\n"
            "Autor: Daniel Riel\n\n"
            "Eine einfache GUI zur Münzerkennung mit Ihrer Webcam.\n"
            "Unterstützt die Sprachen Englisch und Deutsch.\n"
            "Für Support kontaktieren Sie: Daniel.Riel@prosegur.com"
        ),
    },
    "en": {
        "title": "LIVE SCAN",
        "scan": "🔍 Scan Coins",
        "exit": "❌ Exit",
        "total": "TOTAL: €0.00",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
        "exit_dialog_title": "Exit",
        "exit_dialog_text": "Are you sure you want to exit?",
        "file": "File",
        "settings": "Settings",
        "help": "Help",
        "help_dialog_title": "Help",
        "help_dialog_text": (
            "Welcome to CoinScan!\n\n"
            "- Click 'Scan Coins' to start scanning.\n"
            "- Use the blue button to change webcam resolution.\n"
            "- Switch language using the flags.\n"
            "- The program recognizes coins and shows the total.\n\n"
            "For issues, please contact the developer."
        ),
        "about_title": "About CoinScan",
        "about_text": (
            "CoinScan\n"
            "Version: 1.0\n"
            "Author: Daniel Riel\n\n"
            "A simple GUI for coin recognition using your webcam.\n"
            "Supports English and German languages.\n"
            "For support, contact: Daniel.Riel@prosegur.com"
        ),
    },
}


def switch_language(lang, widgets, current_size):
    """
    Update all UI elements to the selected language.
    Ensures the Settings menu is always present after switching languages.
    """
    strings = LANGUAGES.get(lang, LANGUAGES["en"])
    if "title" in widgets:
        widgets["title"].config(text=strings["title"])
    if "scan_button" in widgets:
        widgets["scan_button"].config(text=strings["scan"])
    if "total_label" in widgets:
        widgets["total_label"].config(text=strings["total"])
    if "size_button" in widgets:
        widgets["size_button"].config(
            text=(
                strings["size_plus"]
                if current_size == (320, 240)
                else strings["size_minus"]
            )
        )
    if "file_menu" in widgets:
        menu = widgets["file_menu"]
        idx = widgets.get("file_menu_exit_index", 0)
        try:
            menu.entryconfig(idx, label=strings["exit"])
        except Exception as e:
            print("Menu entry update failed:", e)
    if "help_menu" in widgets:
        help_menu = widgets["help_menu"]
        idx = widgets.get("help_menu_index", 0)
        try:
            help_menu.entryconfig(
                idx,
                label=strings["help"],
                image=widgets.get("help_icon"),
                compound="left",
            )
        except Exception as e:
            print("Help menu entry update failed:", e)
    if "menu_bar" in widgets:
        menu_bar = widgets["menu_bar"]
        # Clear all existing menu entries to avoid duplicates
        try:
            menu_bar.delete(0, "end")
        except Exception as e:
            print("Menu bar clear failed:", e)
        # Re-add File, Settings, and Help menus
        try:
            menu_bar.add_cascade(label=strings["file"], menu=widgets["file_menu"])
            menu_bar.add_cascade(
                label=strings["settings"], menu=widgets["settings_menu"]
            )
            menu_bar.add_cascade(label=strings["help"], menu=widgets["help_menu"])
        except Exception as e:
            print("Menu bar add_cascade failed:", e)