# language.py
# Multilingual UI strings for CoinScan

"""Multilingual UI strings for CoinScan.

Structure:
- LANGUAGES: dict mapping ISO language codes (e.g., 'en', 'de') to dictionaries of UI strings.
- Each inner dictionary contains keys used by the UI:
    - title: main window title or header
    - scan: text for the scan action/button
    - results: label for results section
    - total: formatted total currency string (localized formatting may be applied elsewhere)
    - about: about dialog/menu label
    - exit_confirm: confirmation message shown when user exits

Guidelines for adding languages:
- Use the ISO language code as the top-level key (string).
- Keep keys consistent across languages so the UI lookup is straightforward.
- For currency/number formatting, prefer storing localized strings or use formatting at runtime.
"""

LANGUAGES = {
    "de": {
        # UI header/title shown in the main window
        "title": "LIVE SCAN",
        # Label for the scan button; emoji is supported in most modern UIs
        "scan": "🔍 Münzen scannen",
        # Results section label
        "results": "Ergebnisse",
        # Localized total display — consider formatting dynamically for real values
        "total": "GESAMT: 0,00 €",
        # About dialog/menu label
        "about": "Über CoinScan",
        # Exit confirmation message (German)
        "exit_confirm": "Möchten Sie CoinScan wirklich beenden?",
    },
    "en": {
        # UI header/title shown in the main window
        "title": "LIVE SCAN",
        # Label for the scan button; emoji is supported in most modern UIs
        "scan": "🔍 Scan Coins",
        # Results section label
        "results": "Results",
        # Localized total display — consider formatting dynamically for real values
        "total": "TOTAL: €0.00",
        # About dialog/menu label
        "about": "About CoinScan",
        # Exit confirmation message (English)
        "exit_confirm": "Are you sure you want to exit CoinScan?",
    },
}