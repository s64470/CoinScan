# -*- coding: utf-8 -*-
# language.py

LANGUAGES = {
    "de": {
        "title": "LIVE SCAN",
        "scan": "🔍 Münzen scannen",
        "exit": "❌ Programm Beenden",
        "total": "GESAMT: 0,00 €",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
    },
    "en": {
        "title": "LIVE SCAN",
        "scan": "🔍 Scan Coins",
        "exit": "❌ Exit",
        "total": "TOTAL: €0.00",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
    },
}


def switch_language(lang, widgets, current_size):
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