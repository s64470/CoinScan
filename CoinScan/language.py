from typing import Any, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

"""
language.py

Localized strings and formatting helpers for the CoinScan UI.

Changes:
- Small API helpers added: `get_tooltip`.
- Improved robustness for language lookup and Decimal handling.
- Minor refactor for clarity and constants.
"""

# Default fallback language code
DEFAULT_LANG = "en"

# Translations and UI text for supported languages.
# Keys mirror UI identifiers used across the application.
LANGUAGES: Dict[str, Dict[str, Any]] = {
    "de": {
        "title": "P R O S E G U R",
        "scan": "🔍 Münzen scannen",
        "rescan": "🔁 Erneut scannen",
        "results": "Ergebnisse",
        "total": "GESAMT: 0,00 €",
        "total_fmt": "GESAMT: {amount} €",
        "about": "Über CoinScan",
        "settings": "Einstellungen",
        "close": "Schließen",
        "exit_confirm": "Möchten Sie CoinScan wirklich beenden?",
        "no_coin": "Keine Münze im Zentrum erkannt.",
        "camera_fail": "Kamera konnte nicht geöffnet werden.",
        "frame_fail": "Bild konnte nicht gelesen werden.",
        "tooltips": {
            "scan_btn": "Münzen im Zentrum scannen",
            "size_small": "Webcam-Auflösung 480x360",
            "contrast": "Hochkontrast umschalten",
            "flag_de": "Deutsch wählen",
            "flag_en": "Englisch wählen",
            "home": "Start / Ergebnisse löschen",
            "settings": "Einstellungen öffnen",
            "about": "Info zu CoinScan",
            "exit": "Anwendung beenden",
            "webcam": "Webcam-Vorschau",
            "results_panel": "Erkannte Münzen und Gesamt",
        },
    },
    "en": {
        "title": "P R O S E G U R",
        "scan": "🔍 Scan Coins",
        "rescan": "🔁 Rescan",
        "results": "Results",
        "total": "TOTAL: €0.00",
        "total_fmt": "TOTAL: €{amount}",
        "about": "About CoinScan",
        "settings": "Settings",
        "close": "Close",
        "exit_confirm": "Are you sure you want to exit CoinScan?",
        "no_coin": "No coin detected in centre.",
        "camera_fail": "Camera open failed",
        "frame_fail": "Frame read failed",
        "tooltips": {
            "scan_btn": "Scan coins in centre",
            "size_small": "Set webcam resolution 480x360",
            "contrast": "Toggle high-contrast mode",
            "flag_de": "Switch to German",
            "flag_en": "Switch to English",
            "home": "Home / Clear results",
            "settings": "Open Settings",
            "about": "About CoinScan",
            "exit": "Exit application",
            "webcam": "Webcam preview",
            "results_panel": "Detected coins and totals",
        },
    },
}

# Longer about/help texts per language
ABOUT_TEXTS: Dict[str, str] = {
    "en": (
        "CoinScan is a desktop application designed to help users quickly identify "
        "and count Euro coins using their computer's webcam.\n\n"
        "Key Features:\n"
        "- Live coin scanning and recognition via webcam\n"
        "- Automatic detection of coin type and value\n"
        "- Multilingual interface (English & German)\n"
        "- High-contrast mode for improved accessibility\n"
        "- Simple, intuitive design\n\n"
        "How it works:\n"
        'Place your coins in view of your webcam and click "Scan Coins." CoinScan will '
        "detect coins in the centre of the image, classify them by colour and size, and "
        "display the total value.\n\n"
    ),
    "de": (
        "CoinScan ist eine Desktop-Anwendung, mit der Sie Euro-Münzen schnell "
        "mithilfe der Webcam Ihres Computers erkennen und zählen können.\n\n"
        "Hauptfunktionen:\n"
        "- Live-Erkennung und -Erfassung von Münzen über die Webcam\n"
        "- Automatische Bestimmung von Münztyp und -wert\n"
        "- Mehrsprachige Oberfläche (Englisch & Deutsch)\n"
        "- Hochkontrastmodus für bessere Barrierefreiheit\n"
        "- Einfache, intuitive Bedienung\n\n"
        "So funktioniert's:\n"
        "Legen Sie Ihre Münzen in den Sichtbereich der Webcam und klicken Sie auf "
        "„Münzen scannen“. CoinScan erkennt die Münzen im Bildzentrum, klassifiziert "
        "sie nach Farbe und Größe und zeigt den Gesamtwert an.\n\n"
    ),
}

_DECIMAL_QUANT = Decimal("0.01")


def normalize_lang(lang: Optional[str]) -> str:
    """
    Normalize a language identifier to a supported primary code.

    Examples:
    - "en-US" -> "en"
    - "de_DE" -> "de"

    Returns DEFAULT_LANG when input is falsy or not supported.
    """
    if not lang or not isinstance(lang, str):
        return DEFAULT_LANG

    primary = lang.split("-", 1)[0].split("_", 1)[0].lower()
    return primary if primary in LANGUAGES else DEFAULT_LANG


def get_strings(lang: Optional[str]) -> Dict[str, Any]:
    """
    Return the strings dictionary for the normalized language.
    Always returns a dict (fallback to DEFAULT_LANG).
    """
    return LANGUAGES.get(normalize_lang(lang), LANGUAGES[DEFAULT_LANG])


def get_text(lang: Optional[str], key: str, default: str = "") -> str:
    """
    Retrieve a top-level UI text by key for the given language.
    If the key is missing, return the provided default.
    """
    return get_strings(lang).get(key, default)


def get_tooltip(lang: Optional[str], key: str, default: str = "") -> str:
    """
    Retrieve a tooltip string from the nested 'tooltips' dictionary.
    """
    return get_strings(lang).get("tooltips", {}).get(key, default)


def _to_decimal(amount: Any) -> Decimal:
    """
    Safely convert input to a Decimal rounded to two decimal places.
    Falls back to Decimal('0.00') for invalid inputs.
    """
    try:
        # Use str(amount) to avoid float precision issues when a float is passed.
        d = Decimal(str(amount))
        return d.quantize(_DECIMAL_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


def format_total(lang: Optional[str], amount: Any) -> str:
    """
    Format a numeric amount into the language-specific total string.

    - Rounds to two decimal places using ROUND_HALF_UP.
    - Falls back to 0.00 on invalid input.
    - Uses comma as decimal separator for German ("de").
    - Inserts the formatted amount into the language's "total_fmt".
    """
    strings = get_strings(lang)
    fmt = strings.get("total_fmt", "TOTAL: €{amount}")

    amt = _to_decimal(amount)
    amt_str = format(amt, "0.2f")

    if normalize_lang(lang) == "de":
        amt_str = amt_str.replace(".", ",")

    return fmt.format(amount=amt_str)