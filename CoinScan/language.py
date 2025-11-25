from typing import Any, Dict, Optional, Mapping
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from functools import lru_cache
from types import MappingProxyType


DEFAULT_LANG = "en"


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
SUPPORTED_LANGS = frozenset(LANGUAGES.keys())


@lru_cache(maxsize=32)
def normalize_lang(lang: Optional[str]) -> str:
    if not lang or not isinstance(lang, str):
        return DEFAULT_LANG

    primary = lang.split("-", 1)[0].split("_", 1)[0].lower()
    return primary if primary in SUPPORTED_LANGS else DEFAULT_LANG


@lru_cache(maxsize=32)
def get_strings(lang: Optional[str]) -> Mapping[str, Any]:
    code = normalize_lang(lang)
    return MappingProxyType(LANGUAGES.get(code, LANGUAGES[DEFAULT_LANG]))


def get_text(lang: Optional[str], key: str, default: str = "") -> str:
    return get_strings(lang).get(key, default)


def _to_decimal(amount: Any) -> Decimal:
    try:
        if isinstance(amount, Decimal):
            d = amount
        else:
            d = Decimal(str(amount))
        return d.quantize(_DECIMAL_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


def format_total(lang: Optional[str], amount: Any) -> str:
    strings = get_strings(lang)
    fmt = strings.get("total_fmt", "TOTAL: €{amount}")

    amt = _to_decimal(amount)
    amt_str = format(amt, "0.2f")

    if normalize_lang(lang) == "de":
        amt_str = amt_str.replace(".", ",")

    try:
        return fmt.format(amount=amt_str)
    except Exception:
        return f"TOTAL: €{amt_str}"