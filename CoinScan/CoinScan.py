# -*- coding: utf-8 -*-
import logging
import os
import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Callable, Optional, Tuple, List, Dict, Any
from PIL import Image, ImageDraw, ImageTk
from settings_manager import load_settings, save_settings
from webcam_stream import update_recognition
from language import ABOUT_TEXTS, LANGUAGES
from ui_config import (
    COLORS,
    CONTRAST_ICONS,
    FONTS,
    HIGH_CONTRAST_LOGOS,
    ICON_PATHS,
    SIDEBAR_ICONS,
    SIZES,
)

logger = logging.getLogger(__name__)

VERSION = "1.0.0"
BASE_DIR = os.path.dirname(__file__)


def get_flag_img(path: str) -> ImageTk.PhotoImage:
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        img = Image.new("RGBA", SIZES["flag"], "grey")
        return ImageTk.PhotoImage(img.copy())

    try:
        with Image.open(full_path) as img:
            img = img.convert("RGBA").resize(SIZES["flag"], Image.LANCZOS)
            return ImageTk.PhotoImage(img.copy())
    except Exception as exc:
        logger.debug(
            "Failed to load flag image '%s': %s", full_path, exc, exc_info=True
        )
        img = Image.new("RGBA", SIZES["flag"], "grey")
        return ImageTk.PhotoImage(img.copy())


def load_logo_photo() -> Optional[ImageTk.PhotoImage]:
    size = (SIZES["logo_width"], SIZES["logo_width"])
    png_path = os.path.join(BASE_DIR, "icon", "logo-prosegur.png")
    try:
        if os.path.exists(png_path):
            with Image.open(png_path) as img:
                img = img.convert("RGBA").resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img.copy())

        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        r = size[0] // 2 - 2
        cx = cy = size[0] // 2
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#000000")
        draw.rectangle(
            (cx - r // 3, cy - r // 2, cx - r // 6, cy + r // 2), fill="#FFD100"
        )
        draw.ellipse(
            (cx - r // 6, cy - r // 3, cx + r // 2, cy + r // 3),
            outline="#FFD100",
            width=3,
        )
        return ImageTk.PhotoImage(img.copy())
    except Exception as exc:
        logger.debug("Failed to load or create logo image: %s", exc, exc_info=True)
        return None


def generate_prosegur_globe_bg(
    width: int, height: int, high_contrast: bool = False
) -> Image.Image:
    bg_color = (
        COLORS.get("contrast_bg")
        if high_contrast
        else COLORS.get("background", "#FFD100")
    )
    width = max(2, int(width))
    height = max(2, int(height))
    return Image.new("RGB", (width, height), bg_color)


class Tooltip:
    def __init__(
        self, widget: tk.Widget, text_func: Callable[[], str], delay: int = 400
    ) -> None:
        self.widget = widget
        self.text_func = text_func
        self.delay = int(delay)
        self._id: Optional[str] = None
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide_now)

    def _schedule(self, _event: tk.Event) -> None:
        self._cancel()
        try:
            self._id = self.widget.after(self.delay, self._show)
        except Exception as exc:
            logger.debug("Failed to schedule tooltip: %s", exc, exc_info=True)
            self._id = None

    def _cancel(self) -> None:
        if self._id is not None:
            try:
                self.widget.after_cancel(self._id)
            except Exception as exc:
                logger.debug(
                    "Failed to cancel tooltip scheduling: %s", exc, exc_info=True
                )
            self._id = None

    def _show(self) -> None:
        if self.tip or not self.widget.winfo_exists():
            return
        text = self.text_func()
        if not text:
            return
        try:
            try:
                x, y, cx, cy = (
                    self.widget.bbox("insert")
                    if hasattr(self.widget, "bbox")
                    else (0, 0, 0, 0)
                )
            except Exception:
                x, y, cx, cy = 0, 0, 0, 0
            x += self.widget.winfo_rootx() + 20
            y += self.widget.winfo_rooty() + cy + 20
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(True)
            self.tip.wm_geometry(f"+{x}+{y}")
            frame = tk.Frame(self.tip, bg="#ffffff", bd=1, relief="solid")
            frame.pack(fill="both", expand=True)
            tk.Label(
                frame, text=text, bg="#ffffff", fg="#000000", font=("Segoe UI", 9)
            ).pack(padx=4, pady=2)
        except Exception as exc:
            logger.debug("Failed to show tooltip: %s", exc, exc_info=True)
            self.tip = None

    def _hide_now(self, _event: tk.Event) -> None:
        self._cancel()
        if self.tip:
            try:
                self.tip.destroy()
            except Exception as exc:
                logger.debug("Failed to destroy tooltip: %s", exc, exc_info=True)
            self.tip = None


class CoinScanApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.settings: Dict[str, Any] = load_settings()
        self.current_lang: str = self.settings.get("language", "en")
        webcam_size_key = f"webcam_{self.settings.get('webcam_size', 'small')}"
        self.current_size: Tuple[int, int] = SIZES.get(
            webcam_size_key, SIZES["webcam_small"]
        )
        self.high_contrast: bool = bool(self.settings.get("high_contrast", False))
        self.fullscreen: bool = False

        self.title(f"CoinScan v{VERSION}")

        initial_w = max(1024, int(SIZES.get("window", (1024, 768))[0] * 1.25))
        initial_h = max(800, int(SIZES.get("window", (1024, 768))[1] * 1.25))
        self.geometry(f"{initial_w}x{initial_h}")

        self.update_idletasks()
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        self.create_widgets()
        self.update_language()
        self.apply_contrast()
        self.set_fullscreen(True)

    def create_widgets(self) -> None:
        self.top_bar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48)
        self.top_bar.pack(side="top", fill="x")

        self.logo_photo = load_logo_photo()
        if self.logo_photo is not None:
            self.logo_label = tk.Label(
                self.top_bar, image=self.logo_photo, bg=COLORS["topbar_bg"]
            )
            self.logo_label.pack(side="left")
        else:
            self.logo_label = tk.Label(
                self.top_bar,
                text="PROSEGUR",
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["topbar_bg"],
            )
            self.logo_label.pack(side="left", padx=8)

        self.title_label = tk.Label(
            self.top_bar, font=FONTS["title"], bg=COLORS["topbar_bg"]
        )
        self.title_label.pack(side="left", padx=20)

        topbar_controls = tk.Frame(self.top_bar, bg=COLORS["topbar_bg"])
        topbar_controls.pack(side="right", padx=10)

        self.flag_de = get_flag_img(ICON_PATHS["flag_de"])
        self.flag_en = get_flag_img(ICON_PATHS["flag_en"])

        self.flag_de_btn = tk.Button(
            topbar_controls,
            image=self.flag_de,
            bd=0,
            bg=COLORS["topbar_bg"],
            command=lambda: self.set_language("de"),
        )
        self.flag_de_btn.pack(side="left", padx=2)

        self.flag_en_btn = tk.Button(
            topbar_controls,
            image=self.flag_en,
            bd=0,
            bg=COLORS["topbar_bg"],
            command=lambda: self.set_language("en"),
        )
        self.flag_en_btn.pack(side="left", padx=2)

        self.lang_flag_buttons = {"de": self.flag_de_btn, "en": self.flag_en_btn}
        self.update_flag_buttons()

        tk.Frame(topbar_controls, width=32, bg=COLORS["topbar_bg"]).pack(side="left")

        self.contrast_btn = tk.Button(
            topbar_controls,
            text=CONTRAST_ICONS["normal"],
            bd=0,
            bg=COLORS["topbar_bg"],
            command=self.toggle_contrast,
            font=FONTS["button"],
        )
        self.contrast_btn.pack(side="left", padx=8)

        self.sidebar = tk.Frame(
            self, bg=COLORS["sidebar_bg"], width=SIZES["sidebar_width"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar_buttons: List[tk.Button] = []

        for idx, icon in enumerate(SIDEBAR_ICONS):
            if idx == 3:
                continue
            cmd = {0: self.go_home, 1: self.show_settings, 2: self.show_about}.get(
                idx, None
            )
            btn = tk.Button(
                self.sidebar,
                text=icon,
                font=FONTS["sidebar"],
                bg=COLORS["sidebar_bg"],
                fg=COLORS["sidebar_fg"],
                bd=0,
                relief="flat",
                command=cmd,
            )
            btn.pack(pady=20)
            self.sidebar_buttons.append(btn)

        exit_btn = tk.Button(
            self.sidebar,
            text=SIDEBAR_ICONS[3],
            font=FONTS["sidebar"],
            bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_fg"],
            bd=0,
            relief="flat",
            command=self.confirm_exit,
        )
        exit_btn.pack(side="bottom", pady=20)
        self.sidebar_buttons.append(exit_btn)

        self.main_content = tk.Frame(self, bg=COLORS["background"])
        self.main_content.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        self._bg_image: Optional[ImageTk.PhotoImage] = None
        self.bg_label = tk.Label(self.main_content, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        self.main_content.bind("<Configure>", self._on_main_content_resize)
        self._render_background_image(
            max(2, self.main_content.winfo_width()),
            max(2, self.main_content.winfo_height()),
        )

        self.webcam_panel = tk.Frame(
            self.main_content,
            bg=COLORS["background"],
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground="#000000",
            highlightcolor="#000000",
        )
        self.webcam_panel.pack(side="left", padx=40, pady=40, fill="both", expand=True)

        self.webcam_label = tk.Label(
            self.webcam_panel, bg=COLORS["background"], fg="#000000"
        )
        self.webcam_label.pack(pady=(10, 6))

        # Added: denominations table below webcam_label
        self._create_denominations_table()

        self.brand_right_photo: Optional[ImageTk.PhotoImage] = None
        self.brand_right_label: tk.Label = tk.Label(
            self.main_content, bd=0, bg=COLORS["background"]
        )
        self.brand_right_label.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-48,
            y=-(SIZES.get("footer_height", 30) + 8),
        )

        self.prosegur_globe_right_photo: Optional[ImageTk.PhotoImage] = None
        self.prosegur_globe_right_label: tk.Label = tk.Label(
            self.main_content, bd=0, bg=COLORS["background"]
        )
        self.prosegur_globe_right_label.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-48,
            y=-(SIZES.get("footer_height", 30) + 8),
        )

        self.scan_btn = tk.Button(
            self.webcam_panel,
            font=FONTS["button"],
            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
            fg=COLORS["button_fg"],
            activebackground=COLORS.get(
                "primary_btn_hover", COLORS["button_active_bg"]
            ),
            activeforeground=COLORS["button_active_fg"],
            relief="raised",
            bd=0,
            padx=36,
            pady=12,
            command=self.start_recognition,
        )
        self.scan_btn.pack(pady=(6, 10))

        self.font_frame = tk.Frame(self.webcam_panel, bg=COLORS["background"])
        self.font_frame.pack(pady=(0, 8))
        self.fontsize_label = tk.Label(
            self.font_frame,
            text="Font size",
            bg=COLORS["background"],
            font=FONTS["button"],
        )
        self.fontsize_label.pack(side="left", padx=(0, 10))
        font_group = tk.Frame(self.font_frame, bg=COLORS["background"])
        font_group.pack(side="left")

        self.font_dec_btn = tk.Button(
            font_group,
            text="A-",
            font=FONTS["button"],
            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
            fg=COLORS["button_fg"],
            activebackground=COLORS.get(
                "primary_btn_hover", COLORS["button_active_bg"]
            ),
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=10,
            pady=4,
            command=lambda: self.adjust_font_size(-1),
        )
        self.font_dec_btn.pack(side="left", padx=(0, 4))

        self.font_inc_btn = tk.Button(
            font_group,
            text="A+",
            font=FONTS["button"],
            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
            fg=COLORS["button_fg"],
            activebackground=COLORS.get(
                "font_btn_inc_hover", COLORS["button_active_bg"]
            ),
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=10,
            pady=4,
            command=lambda: self.adjust_font_size(1),
        )
        self.font_inc_btn.pack(side="left", padx=(4, 0))

        self.recognition_list = tk.Listbox(
            self.webcam_panel, font=FONTS["listbox"], height=5, width=50
        )
        self.recognition_list.pack(pady=(0, 8))

        self.detected_coins: List[Dict[str, Any]] = []

        self.edit_frame = tk.Frame(self.webcam_panel, bg=COLORS["background"])
        self.edit_frame.pack(pady=(0, 8))

        self.add_btn = tk.Button(
            self.edit_frame,
            text="Add",
            font=FONTS["button"],
            command=self.add_coin,
            bd=0,
            padx=8,
            pady=4,
        )
        self.add_btn.pack(side="left", padx=4)
        self.edit_btn = tk.Button(
            self.edit_frame,
            text="Edit",
            font=FONTS["button"],
            command=self.edit_selected,
            bd=0,
            padx=8,
            pady=4,
        )
        self.edit_btn.pack(side="left", padx=4)
        self.remove_btn = tk.Button(
            self.edit_frame,
            text="Remove",
            font=FONTS["button"],
            command=self.remove_selected,
            bd=0,
            padx=8,
            pady=4,
        )
        self.remove_btn.pack(side="left", padx=4)
        self.total_btn = tk.Button(
            self.edit_frame,
            text="Total",
            font=FONTS["button"],
            command=self.show_total,
            bd=0,
            padx=8,
            pady=4,
        )
        self.total_btn.pack(side="left", padx=4)

        self.recognition_list.bind("<Double-1>", lambda e: self.edit_selected())

        self.results_panel = tk.Frame(
            self.main_content,
            bg=COLORS["background"],
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground="#000000",
            highlightcolor="#000000",
        )
        self.results_panel.pack(side="right", padx=40, pady=40, fill="y")

        self.results_label = tk.Label(
            self.results_panel, font=FONTS["results"], bg=COLORS["background"]
        )
        self.results_label.pack(pady=(20, 10))

        self.total_label = tk.Label(
            self.results_panel,
            font=FONTS["total"],
            bg=COLORS["background"],
            fg=COLORS["results_fg"],
        )
        self.total_label.pack(pady=(0, 10))

        self.footer = tk.Frame(self, bg=COLORS["footer_bg"])
        self.footer.pack(side="bottom", fill="x")

        self.footer_label = tk.Label(
            self.footer,
            text="© 2025 Prosegur Cash Services Germany GmbH. All rights reserved.",
            font=FONTS["footer"],
            bg=COLORS["footer_bg"],
            fg=COLORS["footer_fg"],
            anchor="w",
            justify="left",
        )
        self.footer_label.pack(padx=16, pady=(0, 4), anchor="w")

        self.set_size(self.current_size)
        self.adjust_font_size(0)

        def tt(key: str) -> Callable[[], str]:
            return lambda: LANGUAGES[self.current_lang].get("tooltips", {}).get(key, "")

        tooltip_obj = globals().get("Tooltip", None)
        if not callable(tooltip_obj):
            logger.error("Tooltip symbol is not callable: %r", tooltip_obj)
            raise TypeError(
                f"Tooltip symbol is not callable: {tooltip_obj!r}. Possible name shadowing or import conflict."
            )

        Tooltip(self.scan_btn, tt("scan_btn"))
        Tooltip(self.contrast_btn, tt("contrast"))

        for child, k in zip(
            topbar_controls.winfo_children()[:2], ["flag_de", "flag_en"]
        ):
            Tooltip(child, tt(k))

        if len(self.sidebar_buttons) >= 4:
            Tooltip(self.sidebar_buttons[0], tt("home"))
            Tooltip(self.sidebar_buttons[1], tt("settings"))
            Tooltip(self.sidebar_buttons[2], tt("about"))
            Tooltip(self.sidebar_buttons[3], tt("exit"))

        Tooltip(self.webcam_label, tt("webcam"))
        Tooltip(self.results_panel, tt("results_panel"))

    def _create_denominations_table(self) -> None:
        """
        Create a simple two-column table with visible lines and static denominations
        (from €2.00 down to €0.01). Placed directly below the webcam label.
        """
        try:
            self.denominations_frame = tk.Frame(
                self.webcam_panel, bg=COLORS["background"]
            )
            # table header
            hdr_font = FONTS.get("button", ("Segoe UI", 10, "bold"))
            cell_font = FONTS.get("listbox", ("Segoe UI", 10))

            header_denom = tk.Label(
                self.denominations_frame,
                text="Denomination",
                font=hdr_font,
                bd=1,
                relief="solid",
                anchor="w",
                padx=6,
            )
            header_qty = tk.Label(
                self.denominations_frame,
                text="Qty",
                font=hdr_font,
                bd=1,
                relief="solid",
                anchor="center",
                padx=6,
            )

            header_denom.grid(row=0, column=0, sticky="ew")
            header_qty.grid(row=0, column=1, sticky="ew")

            denominations = [
                "€2.00",
                "€1.00",
                "€0.50",
                "€0.20",
                "€0.10",
                "€0.05",
                "€0.02",
                "€0.01",
            ]

            rows: List[Tuple[tk.Label, tk.Label]] = []
            for idx, d in enumerate(denominations, start=1):
                lbl_denom = tk.Label(
                    self.denominations_frame,
                    text=d,
                    font=cell_font,
                    bd=1,
                    relief="solid",
                    anchor="w",
                    padx=6,
                )
                lbl_qty = tk.Label(
                    self.denominations_frame,
                    text="0",
                    font=cell_font,
                    bd=1,
                    relief="solid",
                    anchor="center",
                    padx=6,
                )
                lbl_denom.grid(row=idx, column=0, sticky="ew")
                lbl_qty.grid(row=idx, column=1, sticky="ew")
                rows.append((lbl_denom, lbl_qty))

            # make columns expand evenly
            self.denominations_frame.grid_columnconfigure(0, weight=3)
            self.denominations_frame.grid_columnconfigure(1, weight=1)

            self.denominations_frame.pack(pady=(6, 10), fill="x")
            self.denomination_widgets = {"header": (header_denom, header_qty), "rows": rows}
        except Exception as exc:
            logger.debug("Failed to create denominations table: %s", exc, exc_info=True)

    def update_flag_buttons(self) -> None:
        try:
            for lang, btn in getattr(self, "lang_flag_buttons", {}).items():
                if not btn:
                    continue
                if lang == self.current_lang:
                    btn.config(state="disabled", relief="flat")
                else:
                    btn.config(state="normal", relief="raised")
        except Exception as exc:
            logger.debug("Failed to update flag button states: %s", exc, exc_info=True)

    def _on_main_content_resize(self, event: tk.Event) -> None:
        self._render_background_image(max(2, event.width), max(2, event.height))

    def _render_background_image(self, width: int, height: int) -> None:
        try:
            img = generate_prosegur_globe_bg(width, height, self.high_contrast)
            self._bg_image = ImageTk.PhotoImage(img)
            self.bg_label.config(image=self._bg_image)
        except Exception as exc:
            logger.debug("Background rendering failed: %s", exc, exc_info=True)
            try:
                self.bg_label.config(image="")
            except Exception:
                pass

        try:
            if self.high_contrast:
                logo_path = HIGH_CONTRAST_LOGOS.get("prosegur") or os.path.join(
                    BASE_DIR, "icon", "logo-prosegur.png"
                )
            else:
                logo_path = os.path.join(BASE_DIR, "icon", "logo-prosegur.png")

            if logo_path and os.path.exists(logo_path):
                with Image.open(logo_path) as lp:
                    lp = lp.convert("RGBA")
                    side_right = max(80, int(min(width, height) * 0.45))
                    lr = lp.resize((side_right, side_right), Image.LANCZOS).copy()
                    alpha_factor = 0.95 if self.high_contrast else 0.20
                    la = lr.split()[-1].point(lambda v: int(v * alpha_factor))
                    if self.high_contrast:
                        white = Image.new("RGBA", lr.size, (255, 255, 255, 0))
                        white.putalpha(la)
                        lr = white
                    else:
                        r, gch, b, _ = lr.split()
                        lr = Image.merge("RGBA", (r, gch, b, la))

                    self.brand_right_photo = ImageTk.PhotoImage(lr.copy())
                    try:
                        self.brand_right_label.config(
                            image=self.brand_right_photo,
                            bg=(
                                COLORS.get("contrast_panel_bg")
                                if self.high_contrast
                                else COLORS["background"]
                            ),
                        )
                    except Exception:
                        try:
                            self.brand_right_label.config(image=self.brand_right_photo)
                        except Exception as exc:
                            logger.debug(
                                "Failed to set brand_right_label image: %s",
                                exc,
                                exc_info=True,
                            )

                    try:
                        self.brand_right_label.place(
                            relx=1.0,
                            rely=1.0,
                            anchor="se",
                            x=-48,
                            y=-(SIZES.get("footer_height", 30) + 8),
                        )
                        try:
                            self.brand_right_label.lower(self.webcam_panel)
                        except Exception:
                            pass
                    except Exception as exc:
                        logger.debug(
                            "Failed to place brand_right_label: %s", exc, exc_info=True
                        )
            else:
                try:
                    self.brand_right_label.config(image="")
                except Exception:
                    pass
        except Exception as exc:
            logger.debug(
                "Failed while updating right-bottom branding: %s", exc, exc_info=True
            )
            try:
                self.brand_right_label.config(image="")
            except Exception:
                pass

    def set_language(self, lang: str) -> None:
        self.current_lang = lang if lang in LANGUAGES else "en"
        self.settings["language"] = self.current_lang
        save_settings(self.settings)
        self.update_flag_buttons()
        self.update_language()
        self.apply_contrast()

    def set_size(self, size: Tuple[int, int]) -> None:
        self.current_size = size
        for key, val in SIZES.items():
            if val == size and key.startswith("webcam_"):
                self.settings["webcam_size"] = key.replace("webcam_", "")
                break
        else:
            self.settings["webcam_size"] = "small"
        save_settings(self.settings)
        self.resize_window_for_webcam()

    def adjust_font_size(self, delta: int) -> None:
        from tkinter import font as tkfont

        MIN_SIZE = 8
        MAX_SIZE = 28

        def clamp(v: int) -> int:
            return max(MIN_SIZE, min(MAX_SIZE, int(v)))

        def get_current_button_size() -> int:
            f = FONTS.get("button")
            if isinstance(f, tkfont.Font):
                return int(f.cget("size"))
            if isinstance(f, (tuple, list)) and len(f) >= 2 and isinstance(f[1], int):
                return int(f[1])
            return 12

        for key, f in list(FONTS.items()):
            try:
                if isinstance(f, tkfont.Font):
                    current = int(f.cget("size"))
                    f.configure(size=clamp(current + delta))
                elif isinstance(f, tuple) and len(f) >= 2 and isinstance(f[1], int):
                    new_size = clamp(f[1] + delta)
                    FONTS[key] = (f[0], new_size) + tuple(f[2:])
                elif isinstance(f, list) and len(f) >= 2 and isinstance(f[1], int):
                    new_size = clamp(f[1] + delta)
                    FONTS[key] = [f[0], new_size] + f[2:]
            except Exception as exc:
                logger.debug(
                    "Failed to adjust font for key %s: %s", key, exc, exc_info=True
                )
                continue

        size_now = clamp(get_current_button_size())
        self.settings["font_size"] = size_now
        save_settings(self.settings)

        try:
            self.title_label.config(font=FONTS["title"])
            self.scan_btn.config(font=FONTS["button"])
            self.recognition_list.config(font=FONTS["listbox"])
            self.results_label.config(font=FONTS["results"])
            self.total_label.config(font=FONTS["total"])
            self.footer_label.config(font=FONTS["footer"])
            self.contrast_btn.config(font=FONTS["button"])
        except Exception as exc:
            logger.debug("Failed to apply fonts to widgets: %s", exc, exc_info=True)

        if hasattr(self, "font_dec_btn"):
            disabled = size_now <= MIN_SIZE
            self.font_dec_btn.config(
                state=("disabled" if disabled else "normal"),
                bg=(
                    COLORS.get("font_btn_disabled_bg")
                    if disabled
                    else COLORS.get("primary_btn_bg", COLORS["button_bg"])
                ),
                fg=(
                    COLORS.get("font_btn_disabled_fg")
                    if disabled
                    else COLORS["button_fg"]
                ),
                activebackground=COLORS.get(
                    "primary_btn_hover", COLORS["button_active_bg"]
                ),
            )
        if hasattr(self, "font_inc_btn"):
            disabled = size_now >= MAX_SIZE
            self.font_inc_btn.config(
                state=("disabled" if disabled else "normal"),
                bg=(
                    COLORS.get("font_btn_disabled_bg")
                    if disabled
                    else COLORS.get("primary_btn_bg", COLORS["button_bg"])
                ),
                fg=(
                    COLORS.get("font_btn_disabled_fg")
                    if disabled
                    else COLORS["button_fg"]
                ),
                activebackground=COLORS.get(
                    "primary_btn_hover", COLORS["button_active_bg"]
                ),
            )

    def toggle_contrast(self) -> None:
        self.high_contrast = not self.high_contrast
        self.settings["high_contrast"] = self.high_contrast
        save_settings(self.settings)
        self.apply_contrast()

    def apply_contrast(self) -> None:
        if self.high_contrast:
            bg_main = COLORS["contrast_bg"]
            fg_panel = COLORS["contrast_fg"]
            sidebar_bg = COLORS["contrast_sidebar_bg"]
            sidebar_fg = COLORS["contrast_sidebar_fg"]
            contrast_icon = CONTRAST_ICONS["contrast"]
            border_color = COLORS["contrast_fg"]
            listbox_bg = COLORS["contrast_bg"]
            listbox_fg = COLORS["contrast_fg"]
            btn_bg = COLORS["contrast_bg"]
            btn_fg = COLORS["contrast_fg"]
        else:
            bg_main = COLORS["background"]
            fg_panel = "#000000"
            sidebar_bg = COLORS["sidebar_bg"]
            sidebar_fg = COLORS["sidebar_fg"]
            contrast_icon = CONTRAST_ICONS["normal"]
            border_color = "#000000"
            listbox_bg = COLORS.get("listbox_bg", "white")
            listbox_fg = "black"
            btn_bg = COLORS["button_bg"]
            btn_fg = COLORS["button_fg"]

        self.configure(bg=bg_main)
        self.top_bar.config(bg=COLORS["topbar_bg"])
        self.title_label.config(bg=COLORS["topbar_bg"], fg="#000000")

        try:
            if self.high_contrast:
                top_logo_path = (
                    HIGH_CONTRAST_LOGOS.get("prosegur")
                    or ICON_PATHS.get("prosegur")
                    or os.path.join(BASE_DIR, "icon", "logo-prosegur.png")
                )
                if top_logo_path and os.path.exists(top_logo_path):
                    with Image.open(top_logo_path) as li:
                        size = (
                            SIZES.get("logo_width", 50),
                            SIZES.get("logo_width", 50),
                        )
                        iml = li.convert("RGBA").resize(size, Image.LANCZOS)
                        a = iml.split()[-1].point(lambda v: int(v * 0.95))
                        white = Image.new("RGBA", iml.size, (255, 255, 255, 0))
                        white.putalpha(a)
                        self.logo_photo = ImageTk.PhotoImage(white.copy())
                        self.logo_label.config(
                            image=self.logo_photo, bg=COLORS["topbar_bg"]
                        )
                else:
                    self.logo_label.config(bg=COLORS["topbar_bg"])
            else:
                try:
                    self.logo_photo = load_logo_photo()
                    if self.logo_photo is not None:
                        self.logo_label.config(
                            image=self.logo_photo, bg=COLORS["topbar_bg"]
                        )
                    else:
                        self.logo_label.config(bg=COLORS["topbar_bg"])
                except Exception:
                    self.logo_label.config(bg=COLORS["topbar_bg"])
        except Exception as exc:
            logger.debug(
                "Error updating top-bar logo for contrast: %s", exc, exc_info=True
            )
            try:
                self.logo_label.config(bg=COLORS["topbar_bg"])
            except Exception:
                pass

        self.contrast_btn.config(
            bg=COLORS["topbar_bg"], fg="#000000", text=contrast_icon
        )

        self.sidebar.config(bg=sidebar_bg)
        for btn in self.sidebar_buttons:
            btn.config(bg=sidebar_bg, fg=sidebar_fg)

        self.webcam_panel.config(
            bg=bg_main,
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground=border_color,
            highlightcolor=border_color,
        )
        self.font_frame.config(bg=bg_main)
        self.fontsize_label.config(bg=bg_main)
        self.webcam_label.config(bg=bg_main)
        self.recognition_list.config(bg=listbox_bg, fg=listbox_fg)
        self.scan_btn.config(
            bg=COLORS.get("primary_btn_bg", btn_bg),
            fg=btn_fg,
            activebackground=COLORS.get("primary_btn_hover", btn_bg),
            activeforeground=btn_fg,
        )

        # Update denominations table colors if present
        try:
            if hasattr(self, "denomination_widgets"):
                header_bg = COLORS.get("contrast_panel_bg") if self.high_contrast else COLORS["background"]
                header_fg = COLORS.get("contrast_fg") if self.high_contrast else "#000000"
                cell_bg = COLORS.get("contrast_bg") if self.high_contrast else COLORS.get("listbox_bg", "white")
                cell_fg = COLORS.get("contrast_fg") if self.high_contrast else "black"
                hdr_left, hdr_right = self.denomination_widgets["header"]
                try:
                    hdr_left.config(bg=header_bg, fg=header_fg)
                    hdr_right.config(bg=header_bg, fg=header_fg)
                except Exception:
                    pass
                for left, right in self.denomination_widgets["rows"]:
                    try:
                        left.config(bg=cell_bg, fg=cell_fg)
                        right.config(bg=cell_bg, fg=cell_fg)
                    except Exception:
                        pass
        except Exception:
            logger.debug("Failed to update denominations table colors", exc_info=True)

        try:
            if hasattr(self, "font_dec_btn") and hasattr(self, "font_inc_btn"):
                base_font = FONTS.get("button", ("Segoe UI", 14, "bold"))
                if (
                    isinstance(base_font, (tuple, list))
                    and len(base_font) >= 2
                    and isinstance(base_font[1], int)
                ):
                    hc_font = (base_font[0], min(base_font[1] + 4, 40), "bold")
                else:
                    hc_font = base_font

                if self.high_contrast:
                    try:
                        self.font_dec_btn.config(font=hc_font, bg=btn_bg, fg=btn_fg)
                    except Exception:
                        logger.debug(
                            "Failed to configure font_dec_btn for HC", exc_info=True
                        )
                    try:
                        self.font_inc_btn.config(font=hc_font, bg=btn_bg, fg=btn_fg)
                    except Exception:
                        logger.debug(
                            "Failed to configure font_inc_btn for HC", exc_info=True
                        )
                else:
                    std_font = FONTS.get("button")
                    try:
                        self.font_dec_btn.config(
                            font=std_font,
                            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
                            fg=COLORS.get("button_fg", "#FFFFFF"),
                        )
                    except Exception:
                        logger.debug("Failed to restore font_dec_btn", exc_info=True)
                    try:
                        self.font_inc_btn.config(
                            font=std_font,
                            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
                            fg=COLORS.get("button_fg", "#FFFFFF"),
                        )
                    except Exception:
                        logger.debug("Failed to restore font_inc_btn", exc_info=True)
        except Exception:
            logger.debug("Error adjusting A-/A+ buttons for contrast", exc_info=True)

        self.results_panel.config(
            bg=bg_main,
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground=border_color,
            highlightcolor=border_color,
        )

        if self.high_contrast:
            self.results_label.config(bg=COLORS["contrast_panel_bg"], fg=fg_panel)
            self.total_label.config(bg=COLORS["contrast_panel_bg"], fg=fg_panel)
            self.footer.config(bg=COLORS["contrast_panel_bg"])
            try:
                self.footer_label.config(
                    bg=COLORS["contrast_panel_bg"],
                    fg=COLORS.get("contrast_fg", "#FFFF00"),
                )
            except Exception:
                logger.debug("Failed to apply footer_label HC colors", exc_info=True)

            try:
                w = max(2, self.main_content.winfo_width())
                h = max(2, self.main_content.winfo_height())
                side_right = max(96, int(min(w, h) * 0.60))

                hc_logo_path = (
                    HIGH_CONTRAST_LOGOS.get("prosegur")
                    or ICON_PATHS.get("prosegur")
                    or os.path.join(BASE_DIR, "icon", "logo-prosegur.png")
                )

                if hc_logo_path and os.path.exists(hc_logo_path):
                    with Image.open(hc_logo_path) as im:
                        img = im.convert("RGBA").resize(
                            (side_right, side_right), Image.LANCZOS
                        )
                        a = img.split()[-1].point(lambda v: int(v * 0.95))
                        white = Image.new("RGBA", img.size, (255, 255, 255, 0))
                        white.putalpha(a)
                        self.prosegur_globe_right_photo = ImageTk.PhotoImage(
                            white.copy()
                        )
                        try:
                            self.prosegur_globe_right_label.config(
                                bg=COLORS["contrast_panel_bg"],
                                image=self.prosegur_globe_right_photo,
                            )
                        except Exception:
                            try:
                                self.prosegur_globe_right_label.config(
                                    image=self.prosegur_globe_right_photo
                                )
                            except Exception:
                                logger.debug(
                                    "Failed to set prosegur_globe_right_label image",
                                    exc_info=True,
                                )
                        try:
                            self.prosegur_globe_right_label.place(
                                relx=1.0,
                                rely=1.0,
                                anchor="se",
                                x=-48,
                                y=-(SIZES.get("footer_height", 30) + 8),
                            )
                            try:
                                self.prosegur_globe_right_label.lower(self.webcam_panel)
                            except Exception:
                                pass
                        except Exception:
                            logger.debug(
                                "Failed to place prosegur_globe_right_label",
                                exc_info=True,
                            )
                else:
                    try:
                        self.prosegur_globe_right_label.config(image="")
                    except Exception:
                        pass
            except Exception:
                logger.debug(
                    "Error while ensuring HC branding visibility", exc_info=True
                )
                try:
                    self.prosegur_globe_right_label.config(image="")
                except Exception:
                    pass
        else:
            self.results_label.config(bg=COLORS["background"], fg=fg_panel)
            self.total_label.config(bg=COLORS["background"], fg=fg_panel)
            self.footer.config(bg=COLORS["footer_bg"])
            try:
                self.footer_label.config(
                    bg=COLORS["footer_bg"], fg=COLORS.get("footer_fg", "#000000")
                )
            except Exception:
                logger.debug("Failed to restore footer_label colors", exc_info=True)

            try:
                try:
                    self.prosegur_globe_right_label.config(image="")
                except Exception:
                    pass
            except Exception:
                logger.debug(
                    "Failed to regenerate right-bottom globe for normal theme",
                    exc_info=True,
                )
                try:
                    self.prosegur_globe_right_label.config(image="")
                except Exception:
                    pass

    def update_language(self) -> None:
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        self.title_label.config(text=strings.get("title", "CoinScan"))
        self.scan_btn.config(text=strings.get("scan", "Scan"))
        self.results_label.config(text=strings.get("results", "Results"))
        self.total_label.config(text=strings.get("total", "TOTAL: €0.00"))

        if hasattr(self, "recognition_list") and hasattr(self, "detected_coins"):
            self.update_recognition_list()

    def resize_window_for_webcam(self) -> None:
        if getattr(self, "fullscreen", False):
            return

        self.update_idletasks()

        results_w = max(self.results_panel.winfo_reqwidth(), 360)
        margin = 60
        width = (
            SIZES["sidebar_width"]
            + margin
            + self.current_size[0]
            + margin
            + results_w
            + margin
        )
        height = max(
            850,
            self.current_size[1]
            + margin
            + margin
            + 48
            + SIZES.get("footer_height", 30),
        )

        self.geometry(f"{width}x{height}")

    def start_recognition(self) -> None:
        update_recognition(
            self.scan_btn,
            self.recognition_list,
            self.total_label,
            self.webcam_label,
            self.current_size,
            self.current_lang,
            on_results=self.handle_recognition_results,
        )

    def handle_recognition_results(self, results: List[Any]) -> None:
        new_coins: List[Dict[str, Any]] = []
        try:
            for r in results:
                try:
                    value = float(r[0])
                except Exception:
                    continue
                new_coins.append({"value": value})
        except Exception as exc:
            logger.debug(
                "Unexpected structure in recognition results: %s", exc, exc_info=True
            )
            new_coins = []

        try:
            for coin in new_coins:
                if coin not in self.detected_coins:
                    self.detected_coins.append(coin)
        except Exception as exc:
            logger.debug(
                "Failed appending new coins, replacing list: %s", exc, exc_info=True
            )
            self.detected_coins = new_coins

        self.update_recognition_list()

    def show_about(self) -> None:
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        about_win = tk.Toplevel(self)
        about_win.title(strings.get("about", "About CoinScan"))
        about_win.resizable(False, False)
        about_win.configure(bg=COLORS["background"])
        tk.Label(
            about_win,
            text=strings.get("about", "About CoinScan"),
            font=FONTS["about_title"],
            bg=COLORS["background"],
        ).pack(padx=20, pady=(20, 5))
        tk.Label(
            about_win,
            text=f"Version: {VERSION}",
            font=FONTS["version"],
            bg=COLORS["background"],
            fg=COLORS["sidebar_bg"],
        ).pack(padx=20, pady=(0, 10))
        tk.Message(
            about_win,
            text=ABOUT_TEXTS.get(self.current_lang, ABOUT_TEXTS["en"]),
            font=FONTS["about_text"],
            bg=COLORS["background"],
            width=400,
        ).pack(padx=20, pady=(0, 20))
        tk.Button(
            about_win,
            text=strings.get("close", "Close"),
            command=about_win.destroy,
            font=FONTS["about_button"],
        ).pack(pady=(0, 20))

    def show_settings(self) -> None:
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        settings_win = tk.Toplevel(self)
        settings_win.title(strings.get("settings", "Settings"))
        settings_win.resizable(False, False)
        settings_win.configure(bg=COLORS["background"])
        tk.Label(
            settings_win,
            text=strings.get("settings", "Settings"),
            font=FONTS["about_title"],
            bg=COLORS["background"],
        ).pack(padx=20, pady=(20, 10))
        tk.Label(
            settings_win,
            text="(Settings options go here)",
            font=FONTS["about_text"],
            bg=COLORS["background"],
        ).pack(padx=20, pady=(0, 20))
        tk.Button(
            settings_win,
            text=strings.get("close", "Close"),
            command=settings_win.destroy,
            font=FONTS["about_button"],
        ).pack(pady=(0, 20))

    def confirm_exit(self) -> None:
        confirm_text = LANGUAGES.get(self.current_lang, LANGUAGES["en"]).get(
            "exit_confirm", "Are you sure you want to exit CoinScan?"
        )
        if messagebox.askokcancel("Exit", confirm_text):
            self.quit()

    def go_home(self) -> None:
        self.recognition_list.delete(0, "end")
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        self.total_label.config(text=strings.get("total", "TOTAL: €0.00"))
        self.webcam_label.config(image="")

    def set_fullscreen(self, enable: bool = True) -> None:
        self.fullscreen = bool(enable)
        try:
            self.attributes("-fullscreen", self.fullscreen)
        except Exception:
            self.state("zoomed" if self.fullscreen else "normal")

    def toggle_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(not self.fullscreen)

    def exit_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(False)

    def add_coin(self) -> None:
        dlg = CoinEditDialog(self)
        result = dlg.show()
        if result and isinstance(result, dict):
            try:
                result["value"] = float(result["value"])
            except Exception:
                result["value"] = 0.0
            self.detected_coins.append(result)
            self.update_recognition_list()

    def edit_selected(self) -> None:
        try:
            selection = self.recognition_list.curselection()
            if not selection:
                return
            index = selection[0]
            current = self.detected_coins[index]
            dlg = CoinEditDialog(self, coin=current)
            result = dlg.show()
            if result and isinstance(result, dict):
                try:
                    result["value"] = float(result["value"])
                except Exception:
                    result["value"] = 0.0
                self.detected_coins[index] = result
                self.update_recognition_list()
        except Exception as exc:
            logger.debug("Failed to edit selected coin: %s", exc, exc_info=True)

    def remove_selected(self) -> None:
        try:
            selection = self.recognition_list.curselection()
            if not selection:
                return
            index = selection[0]
            del self.detected_coins[index]
            self.update_recognition_list()
        except Exception as exc:
            logger.debug("Failed to remove selected coin: %s", exc, exc_info=True)

    def get_total_value(self) -> float:
        total = 0.0
        for coin in getattr(self, "detected_coins", []):
            v = coin.get("value", 0)
            try:
                total += float(v)
            except Exception:
                continue
        return total

    def show_total(self) -> None:
        total = self.get_total_value()
        messagebox.showinfo("Total", f"TOTAL: €{total:.2f}", parent=self)

    def update_recognition_list(self) -> None:
        try:
            self.recognition_list.delete(0, "end")
            for coin in self.detected_coins:
                try:
                    value = float(coin.get("value", 0))
                except Exception:
                    value = 0.0
                label = f"€{value:.2f}"
                self.recognition_list.insert("end", label)

            total_value = self.get_total_value()
            self.total_label.config(text=f"TOTAL: €{total_value:.2f}")
        except Exception as exc:
            logger.debug("Failed to update recognition list: %s", exc, exc_info=True)


class CoinEditDialog:
    def __init__(
        self, parent: tk.Widget, coin: Optional[Dict[str, Any]] = None
    ) -> None:
        self.parent = parent
        self.coin = coin

        self.win = tk.Toplevel(parent)
        self.win.title("Edit Coin Entry")
        self.win.configure(bg=COLORS["background"])
        self.win.transient(parent)
        self.win.grab_set()

        dlg_w = 460
        dlg_h = 160
        try:
            self.win.update_idletasks()
            pw = parent.winfo_width() or self.win.winfo_screenwidth()
            ph = parent.winfo_height() or self.win.winfo_screenheight()
            px = parent.winfo_rootx() or 0
            py = parent.winfo_rooty() or 0
            x = px + max(0, (pw - dlg_w) // 2)
            y = py + max(0, (ph - dlg_h) // 2)
            self.win.geometry(f"{dlg_w}x{dlg_h}+{x}+{y}")
        except Exception as exc:
            logger.debug("Failed to position dialog: %s", exc, exc_info=True)
            self.win.geometry(f"{dlg_w}x{dlg_h}")

        self.win.resizable(False, False)

        self.form_frame = tk.Frame(self.win, bg=COLORS["background"])
        self.form_frame.pack(padx=20, pady=16, fill="both", expand=True)

        tk.Label(
            self.form_frame,
            text="Value (in €):",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10), padx=(0, 6))

        self.value_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 12),
            fg="#000000",
            bd=1,
            relief="solid",
            width=28,
        )
        self.value_entry.grid(row=0, column=1, pady=(0, 10), sticky="w")

        self.button_frame = tk.Frame(self.win, bg=COLORS["background"])
        self.button_frame.pack(pady=(0, 12), padx=20, anchor="e")

        tk.Button(
            self.button_frame,
            text="OK",
            command=self.on_ok,
            font=FONTS["button"],
            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
            fg=COLORS["button_fg"],
            activebackground=COLORS.get(
                "primary_btn_hover", COLORS["button_active_bg"]
            ),
            activeforeground=(
                COLORS.get("primary_btn_active_fg", COLORS["button_active_fg"])
                if "primary_btn_active_fg" in COLORS
                else COLORS.get("button_active_fg")
            ),
            bd=0,
            padx=18,
            pady=8,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            self.button_frame,
            text="Cancel",
            command=self.on_cancel,
            font=FONTS["button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            bd=0,
            padx=18,
            pady=8,
        ).pack(side="right", padx=(0, 8))

        if coin:
            self.value_entry.insert(0, str(coin.get("value", "")))

        self.win.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.value_entry.focus_set()

    def show(self) -> Optional[Dict[str, Any]]:
        self.win.deiconify()
        self.parent.wait_window(self.win)
        return getattr(self, "result", None)

    def on_ok(self) -> None:
        try:
            value = float(self.value_entry.get())
            self.result = {"value": value}
            self.win.destroy()
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Please enter valid values for all fields.",
                parent=self.win,
            )

    def on_cancel(self) -> None:
        self.win.destroy()


if __name__ == "__main__":
    app = CoinScanApp()
    app.mainloop()