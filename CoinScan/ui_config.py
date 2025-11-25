from pathlib import Path
from typing import Final, Mapping, Tuple, Union, Dict


FontDef = Tuple[Union[str, int], ...]
SizeDef = Union[Tuple[int, int], int]

LOGO_WIDTH: Final[int] = 50

COLORS: Final[Mapping[str, str]] = {
    "background": "#FFD100",
    "panel_bg": "#FFFFFF",
    "sidebar_bg": "#2c3e50",
    "sidebar_fg": "#FFFFFF",
    "topbar_bg": "#F5C800",
    "button_bg": "#3498db",
    "button_fg": "#FFFFFF",
    "button_active_bg": "#2980b9",
    "button_active_fg": "#FFFFFF",
    "results_fg": "#3498db",
    "footer_bg": "#FFD100",
    "footer_fg": "#000000",
    "listbox_bg": "#FFE680",
    "contrast_bg": "#000000",
    "contrast_fg": "#FFFF00",
    "contrast_panel_bg": "#000000",
    "contrast_sidebar_bg": "#000000",
    "contrast_sidebar_fg": "#FFFF00",
    "primary_btn_bg": "#0057B7",
    "primary_btn_hover": "#004C9F",
    "font_btn_inc_bg": "#2ecc71",
    "font_btn_inc_hover": "#27ae60",
    "font_btn_dec_bg": "#e67e22",
    "font_btn_dec_hover": "#d35400",
    "font_btn_disabled_bg": "#000000",
    "font_btn_disabled_fg": "#FFFF00",
}

FONTS: Final[Mapping[str, FontDef]] = {
    "title": ("Segoe UI", 18, "bold"),
    "sidebar": ("Segoe UI", 16),
    "version": ("Segoe UI", 10, "bold"),
    "button": ("Segoe UI", 14, "bold"),
    "results": ("Segoe UI", 14, "bold"),
    "total": ("Segoe UI", 16, "bold"),
    "listbox": ("Segoe UI", 12),
    "about_title": ("Segoe UI", 16, "bold"),
    "about_text": ("Segoe UI", 11),
    "about_button": ("Segoe UI", 11),
    "size_button": ("Segoe UI", 12),
    "footer": ("Segoe UI", 8),
}

ICON_DIR: Final[Path] = (Path(__file__).parent / "icon").resolve(strict=False)

_ICON_FILES: Final[Mapping[str, str]] = {
    "flag_de": "flag_DE.png",
    "flag_en": "flag_UK.png",
    "prosegur": "prosegur.png",
    "prosegur_globe": "prosegur_globe.png",
}

ICON_PATHS: Final[Dict[str, str]] = {
    key: str((ICON_DIR / filename).resolve(strict=False))
    for key, filename in _ICON_FILES.items()
}

HIGH_CONTRAST_LOGOS: Final[Mapping[str, str]] = {
    "prosegur": ICON_PATHS.get("prosegur_globe", "")
}

SIZES: Final[Mapping[str, SizeDef]] = {
    "window": (1600, 950),
    "webcam_small": (480, 360),
    "webcam_large": (800, 600),
    "webcam_xl": (1280, 960),
    "flag": (24, 24),
    "sidebar_width": LOGO_WIDTH,
    "logo_width": LOGO_WIDTH,
    "footer_height": 30,
}

SIDEBAR_ICONS: Final[Tuple[str, ...]] = (
    "\U0001f3e0",
    "\u2699\ufe0f",
    "\u2753",
    "\u23fb",
)

CONTRAST_ICONS: Final[Mapping[str, str]] = {
    "normal": "\U0001f313",
    "contrast": "\u2600\ufe0f",
}


def icon_path(name: str) -> str:
    return ICON_PATHS.get(name, "")


def icon_exists(name: str) -> bool:
    p = icon_path(name)
    if not p:
        return False
    try:
        return Path(p).is_file()
    except OSError:
        return False


def available_icons() -> Tuple[str, ...]:
    return tuple(ICON_PATHS.keys())


__all__ = [
    "LOGO_WIDTH",
    "COLORS",
    "FONTS",
    "ICON_DIR",
    "ICON_PATHS",
    "HIGH_CONTRAST_LOGOS",
    "SIZES",
    "SIDEBAR_ICONS",
    "CONTRAST_ICONS",
    "icon_path",
    "icon_exists",
    "available_icons",
]