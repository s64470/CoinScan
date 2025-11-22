import os
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
from typing import Optional, Callable, Tuple
from settings_manager import load_settings, save_settings, DEFAULT_SETTINGS

from webcam_stream import update_recognition
from language import LANGUAGES, ABOUT_TEXTS
from ui_config import (
    COLORS,
    FONTS,
    ICON_PATHS,
    HIGH_CONTRAST_LOGOS,
    SIZES,
    SIDEBAR_ICONS,
    CONTRAST_ICONS,
)

VERSION = "1.0.0"


# Load a flag image from disk and return a Tk PhotoImage (fallback to grey box).
def get_flag_img(path: str) -> ImageTk.PhotoImage:
    base = os.path.dirname(__file__)
    full_path = os.path.join(base, path)
    try:
        with Image.open(full_path) as img:
            img = img.convert("RGBA").resize(SIZES["flag"], Image.LANCZOS)
            return ImageTk.PhotoImage(img.copy())
    except (FileNotFoundError, OSError):
        img = Image.new("RGBA", SIZES["flag"], "grey")
        return ImageTk.PhotoImage(img)
    except Exception:
        img = Image.new("RGBA", SIZES["flag"], "grey")
        return ImageTk.PhotoImage(img)


# Load application logo if present, otherwise draw a simple fallback logo.
def load_logo_photo() -> Optional[ImageTk.PhotoImage]:
    base = os.path.dirname(__file__)
    size = (SIZES["logo_width"], SIZES["logo_width"])
    png_path = os.path.join(base, "icon", "logo-prosegur.png")
    if os.path.exists(png_path):
        try:
            with Image.open(png_path) as img:
                img = img.convert("RGBA").resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img.copy())
        except (OSError, FileNotFoundError):
            pass
        except Exception:
            pass
    try:
        # Draw a simple circular fallback logo
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = size[0] // 2 - 2
        cx = cy = size[0] // 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#000000")
        d.rectangle(
            (cx - r // 3, cy - r // 2, cx - r // 6, cy + r // 2), fill="#FFD100"
        )
        d.ellipse(
            (cx - r // 6, cy - r // 3, cx + r // 2, cy + r // 3),
            outline="#FFD100",
            width=3,
        )
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# Generate a background image with a faint logo composited in the corner.
def generate_prosegur_globe_bg(
    width: int, height: int, high_contrast: bool = False
) -> Image.Image:
    """Generate a background with a faint Prosegur globe.

    When `high_contrast` is True the background color and globe are adapted for
    high-contrast mode (black background and an inverted globe image).
    """
    bg_color = (
        COLORS.get("contrast_bg")
        if high_contrast
        else COLORS.get("background", "#FFD100")
    )
    width = max(2, int(width))
    height = max(2, int(height))
    base = Image.new("RGB", (width, height), bg_color).convert("RGBA")

    # Previously a faint Prosegur globe was composited into the background.
    # This function now returns a plain background color without additional
    # decorative imagery so branding is handled by the explicit right-bottom
    # logo placed in the UI instead.
    return base.convert("RGB")


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, int(alpha))


# Draw a small globe icon used in the footer.
def generate_globe_icon(
    diameter: int = 40, stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
) -> Image.Image:
    diameter = max(16, int(diameter))
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = diameter // 2 - 2
    cx = cy = diameter // 2
    stroke = stroke_color
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius), outline=stroke, width=3
    )
    # Draw globe longitude lines
    for offset in (-0.45, 0, 0.45):
        ox = int(radius * offset)
        draw.ellipse(
            (cx - ox - radius, cy - radius, cx - ox + radius, cy + radius),
            outline=stroke,
            width=1,
        )
    # Draw globe latitude lines
    for frac in (-0.5, 0, 0.5):
        ry = int(radius * (0.65 + 0.25 * frac))
        draw.ellipse(
            (cx - radius, cy - ry, cx + radius, cy + ry), outline=stroke, width=1
        )
    draw.line([(cx - radius, cy), (cx + radius, cy)], fill=stroke, width=2)
    return img


# Simple tooltip helper for widgets.
class Tooltip:
    def __init__(self, widget: tk.Widget, text_func: Callable[[], str], delay: int = 400) -> None:
        # Save state and bind enter/leave events.
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self._id: Optional[str] = None
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide_now)

    # Schedule tooltip display after delay.
    def _schedule(self, _event: tk.Event) -> None:
        self._cancel()
        self._id = self.widget.after(self.delay, self._show)

    # Cancel a scheduled tooltip show.
    def _cancel(self) -> None:
        if self._id is not None:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    # Create and show the tooltip window.
    def _show(self) -> None:
        if self.tip or not self.widget.winfo_exists():
            return
        text = self.text_func()
        if not text:
            return
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

    # Hide and destroy the tooltip immediately.
    def _hide_now(self, _event: tk.Event) -> None:
        self._cancel()
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


_InternalTooltip = Tooltip


# Main application window.
class CoinScanApp(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        # Load and apply saved settings.
        self.settings = load_settings()
        self.current_lang = self.settings.get("language", "en")
        webcam_size_key = f"webcam_{self.settings.get('webcam_size', 'small')}"
        self.current_size = SIZES.get(webcam_size_key, SIZES["webcam_small"])
        self.high_contrast = self.settings.get("high_contrast", False)
        self.font_size = self.settings.get("font_size", 14)
        self.fullscreen = False

        # Window setup
        self.title(f"CoinScan v{VERSION}")
        self.geometry(f"{SIZES['window'][0]}x{SIZES['window'][1]}")
        self.update_idletasks()
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Build UI and apply preferences
        self.create_widgets()
        self.update_language()
        self.apply_contrast()
        self.set_fullscreen(True)

    # Create and arrange all widgets.
    def create_widgets(self) -> None:

        # Top bar with logo and controls
        self.top_bar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48)
        self.top_bar.pack(side="top", fill="x")

        self.logo_photo = load_logo_photo()
        if self.logo_photo is not None:
            self.logo_label = tk.Label(
                self.top_bar, image=self.logo_photo, bg=COLORS["topbar_bg"]
            )
            self.logo_label.pack(side="left", padx=(0, 0))
        else:
            # Text fallback for the logo
            self.logo_label = tk.Label(
                self.top_bar,
                text="PROSEGUR",
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["topbar_bg"],
            )
            self.logo_label.pack(side="left", padx=(8, 0))

        # Title label in top bar
        self.title_label = tk.Label(
            self.top_bar, font=FONTS["title"], bg=COLORS["topbar_bg"]
        )
        self.title_label.pack(side="left", padx=20)

        # Controls on the top-right (language flags, contrast)
        topbar_controls = tk.Frame(self.top_bar, bg=COLORS["topbar_bg"])
        topbar_controls.pack(side="right", padx=10)

        # Load flag images for language selection
        self.flag_de = get_flag_img(ICON_PATHS["flag_de"])
        self.flag_en = get_flag_img(ICON_PATHS["flag_en"])

        tk.Button(
            topbar_controls,
            image=self.flag_de,
            bd=0,
            bg=COLORS["topbar_bg"],
            command=lambda: self.set_language("de"),
        ).pack(side="left", padx=2)
        tk.Button(
            topbar_controls,
            image=self.flag_en,
            bd=0,
            bg=COLORS["topbar_bg"],
            command=lambda: self.set_language("en"),
        ).pack(side="left", padx=2)

        tk.Frame(topbar_controls, width=32, bg=COLORS["topbar_bg"]).pack(side="left")

        # Contrast toggle button
        self.contrast_btn = tk.Button(
            topbar_controls,
            text=CONTRAST_ICONS["normal"],
            bd=0,
            bg=COLORS["topbar_bg"],
            command=self.toggle_contrast,
            font=FONTS["button"],
        )
        self.contrast_btn.pack(side="left", padx=8)

        # Sidebar with navigation buttons
        self.sidebar = tk.Frame(
            self, bg=COLORS["sidebar_bg"], width=SIZES["sidebar_width"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar_buttons = []

        for idx, icon in enumerate(SIDEBAR_ICONS):
            if idx == 3:
                continue

            if idx == 0:
                cmd = self.go_home
            elif idx == 1:
                cmd = self.show_settings
            elif idx == 2:
                cmd = self.show_about
            else:
                cmd = None

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

        # Exit button at the bottom of sidebar
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

        # Main content area
        self.main_content = tk.Frame(self, bg=COLORS["background"])
        self.main_content.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        # Background image label (kept behind other widgets)
        self._bg_image: Optional[ImageTk.PhotoImage] = None
        self.bg_label = tk.Label(self.main_content, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        # Re-render background when the main content is resized
        self.main_content.bind("<Configure>", self._on_main_content_resize)
        self._render_background_image(
            max(2, self.main_content.winfo_width()),
            max(2, self.main_content.winfo_height()),
        )

        # Left panel: webcam and controls
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

        # Label to show webcam image
        self.webcam_label = tk.Label(
            self.webcam_panel, bg=COLORS["background"], fg="#000000"
        )
        self.webcam_label.pack(pady=(10, 6))

        # Branding logo placed at the right-bottom behind the webcam panel.
        # This is intentionally behind the webcam so it doesn't obstruct content.
        self.brand_right_photo: Optional[ImageTk.PhotoImage] = None
        self.brand_right_label: Optional[tk.Label] = tk.Label(
            self.main_content, bd=0, bg=COLORS["background"]
        )
        self.brand_right_label.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-48,
            y=-(SIZES.get("footer_height", 30) + 8),
        )

        # Scan button starts recognition
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

        # Font size controls
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

        # Listbox showing recognition results
        self.recognition_list = tk.Listbox(
            self.webcam_panel, font=FONTS["listbox"], height=5, width=50
        )
        self.recognition_list.pack(pady=(0, 8))

        # Internal model for detected coins to support manual post-processing.
        # Each entry is a dict: {value, label, colour, radius, hue}
        self.detected_coins: list[dict] = []

        # Manual edit controls (Add / Edit / Remove)
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

        # Double-click to edit an entry for convenience
        self.recognition_list.bind("<Double-1>", lambda e: self.edit_selected())

        # Right panel: results summary
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

        # Footer with a small globe icon and copyright label
        self.footer = tk.Frame(self, bg=COLORS["footer_bg"])
        self.footer.pack(side="bottom", fill="x")

        try:
            globe_img = generate_globe_icon(64)
            self.footer_globe_photo = ImageTk.PhotoImage(globe_img)
            self.footer_globe_label = tk.Label(
                self.footer, image=self.footer_globe_photo, bg=COLORS["footer_bg"]
            )

            self.footer_globe_label.place(relx=1.0, rely=1.0, anchor="se", x=-16, y=-4)
        except Exception:
            self.footer_globe_label = None

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

        # Apply size and font preferences
        self.set_size(self.current_size)

        self.adjust_font_size(0)

        # Helper to get tooltip text for a key
        def tt(key: str) -> Callable[[], str]:
            return lambda: LANGUAGES[self.current_lang].get("tooltips", {}).get(key, "")

        # Verify the Tooltip symbol is callable to avoid conflicts
        tooltip_obj = globals().get("Tooltip", None)
        if not callable(tooltip_obj):
            import logging

            logger = logging.getLogger(__name__)
            logger.error("Tooltip symbol is not callable: %r", tooltip_obj)
            raise TypeError(
                f"Tooltip symbol is not callable: {tooltip_obj!r}. "
                "Possible name shadowing or import conflict. "
                "Inspect where `Tooltip` is defined or overwritten."
            )

        # Attach tooltips to important controls
        _InternalTooltip(self.scan_btn, tt("scan_btn"))
        _InternalTooltip(self.contrast_btn, tt("contrast"))

        for child, k in zip(
            topbar_controls.winfo_children()[:2], ["flag_de", "flag_en"]
        ):
            Tooltip(child, tt(k))
        Tooltip(self.sidebar_buttons[0], tt("home"))
        Tooltip(self.sidebar_buttons[1], tt("settings"))
        Tooltip(self.sidebar_buttons[2], tt("about"))
        Tooltip(self.sidebar_buttons[3], tt("exit"))
        Tooltip(self.webcam_label, tt("webcam"))
        Tooltip(self.results_panel, tt("results_panel"))

    # Handle resizing of the main content (recreate background unless in high contrast).
    def _on_main_content_resize(self, event: tk.Event) -> None:

        # Always re-render the background image on resize. The generator decides
        # whether to produce a high-contrast background based on current state.
        self._render_background_image(max(2, event.width), max(2, event.height))

    # Render and set the background image on the bg_label.
    def _render_background_image(self, width: int, height: int) -> None:
        try:
            img = generate_prosegur_globe_bg(
                width, height, getattr(self, "high_contrast", False)
            )
            self._bg_image = ImageTk.PhotoImage(img)
            self.bg_label.config(image=self._bg_image)
            # Place a branding logo behind the webcam at the right-bottom if the
            # file `icon/logo-prosegur.png` (or a high-contrast alternative) is present.
            try:
                if getattr(self, "high_contrast", False):
                    logo_path = HIGH_CONTRAST_LOGOS.get("prosegur") or os.path.join(
                        os.path.dirname(__file__), "icon", "logo-prosegur.png"
                    )
                else:
                    logo_path = os.path.join(
                        os.path.dirname(__file__), "icon", "logo-prosegur.png"
                    )

                if logo_path and os.path.exists(logo_path):
                    with Image.open(logo_path) as lp:
                        lp = lp.convert("RGBA")
                        side_right = max(80, int(min(width, height) * 0.45))
                        lr = lp.resize((side_right, side_right), Image.LANCZOS).copy()
                        alpha_factor = (
                            0.95 if getattr(self, "high_contrast", False) else 0.20
                        )
                        la = lr.split()[-1].point(lambda v: int(v * alpha_factor))
                        if getattr(self, "high_contrast", False):
                            # Make a white silhouette for high-contrast
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
                                    if getattr(self, "high_contrast", False)
                                    else COLORS["background"]
                                ),
                            )
                        except Exception:
                            try:
                                self.brand_right_label.config(
                                    image=self.brand_right_photo
                                )
                            except Exception:
                                pass

                        # Place and ensure it's behind the webcam panel
                        try:
                            self.brand_right_label.place(
                                relx=1.0,
                                rely=1.0,
                                anchor="se",
                                x=-48,
                                y=-(SIZES.get("footer_height", 30) + 8),
                            )
                            self.brand_right_label.lower(self.webcam_panel)
                        except Exception:
                            pass
                else:
                    try:
                        self.brand_right_label.config(image="")
                    except Exception:
                        pass
            except Exception:
                try:
                    self.brand_right_label.config(image="")
                except Exception:
                    pass
            # No additional compositing or branding on the background image.
            # Background is set above and decorative globe elements have been removed.
        except Exception:
            self.bg_label.config(image="/")

    # Change language and persist setting.
    def set_language(self, lang: str) -> None:

        self.current_lang = lang if lang in LANGUAGES else "en"

        self.settings["language"] = self.current_lang
        save_settings(self.settings)

        self.update_language()
        self.apply_contrast()

    # Set webcam size, persist and resize window accordingly.
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

    # Adjust all fonts by delta and update controls.
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

        # Update the FONTS mapping in-place with clamped sizes.
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
            except Exception:
                continue

        size_now = clamp(get_current_button_size())
        self.settings["font_size"] = size_now
        save_settings(self.settings)

        # Apply fonts to widgets (best-effort).
        try:
            self.title_label.config(font=FONTS["title"])
            self.scan_btn.config(font=FONTS["button"])
            self.recognition_list.config(font=FONTS["listbox"])
            self.results_label.config(font=FONTS["results"])
            self.total_label.config(font=FONTS["total"])
            self.footer_label.config(font=FONTS["footer"])
            self.contrast_btn.config(font=FONTS["button"])
        except Exception:
            pass

        # Enable/disable font change buttons based on limits.
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

    # Toggle high-contrast mode and persist.
    def toggle_contrast(self) -> None:

        self.high_contrast = not self.high_contrast

        self.settings["high_contrast"] = self.high_contrast
        save_settings(self.settings)

        self.apply_contrast()

    # Apply color scheme depending on high_contrast flag.
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

        # Update widget colors
        self.configure(bg=bg_main)
        self.top_bar.config(bg=COLORS["topbar_bg"])
        self.title_label.config(bg=COLORS["topbar_bg"], fg="#000000")
        # Update top-bar logo for high-contrast: use a white silhouette when enabled
        try:
            if getattr(self, "high_contrast", False):
                top_logo_path = (
                    HIGH_CONTRAST_LOGOS.get("prosegur")
                    or ICON_PATHS.get("prosegur")
                    or os.path.join(
                        os.path.dirname(__file__), "icon", "logo-prosegur.png"
                    )
                )
                if top_logo_path and os.path.exists(top_logo_path):
                    with Image.open(top_logo_path) as li:
                        size = (
                            SIZES.get("logo_width", 50),
                            SIZES.get("logo_width", 50),
                        )
                        iml = li.convert("RGBA").resize(size, Image.LANCZOS)
                        # create white silhouette preserving alpha
                        a = iml.split()[-1].point(lambda v: int(v * 0.95))
                        white = Image.new("RGBA", iml.size, (255, 255, 255, 0))
                        white.putalpha(a)
                        self.logo_photo = ImageTk.PhotoImage(white.copy())
                        self.logo_label.config(
                            image=self.logo_photo, bg=COLORS["topbar_bg"]
                        )
                else:
                    # fallback: just set bg
                    self.logo_label.config(bg=COLORS["topbar_bg"])
            else:
                # restore standard logo
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
        except Exception:
            # Ensure at least the background is updated
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

        # Adjust A- / A+ buttons' font for high-contrast accessibility and
        # restore standard font when not in high-contrast.
        try:
            if hasattr(self, "font_dec_btn") and hasattr(self, "font_inc_btn"):
                base_font = FONTS.get("button", ("Segoe UI", 14, "bold"))
                if (
                    isinstance(base_font, (tuple, list))
                    and len(base_font) >= 2
                    and isinstance(base_font[1], int)
                ):
                    # Increase size for high-contrast to improve legibility
                    hc_font = (base_font[0], min(base_font[1] + 4, 40), "bold")
                else:
                    hc_font = base_font

                if getattr(self, "high_contrast", False):
                    try:
                        self.font_dec_btn.config(font=hc_font, bg=btn_bg, fg=btn_fg)
                    except Exception:
                        pass
                    try:
                        self.font_inc_btn.config(font=hc_font, bg=btn_bg, fg=btn_fg)
                    except Exception:
                        pass
                else:
                    std_font = FONTS.get("button")
                    try:
                        self.font_dec_btn.config(
                            font=std_font,
                            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
                            fg=COLORS.get("button_fg", "#FFFFFF"),
                        )
                    except Exception:
                        pass
                    try:
                        self.font_inc_btn.config(
                            font=std_font,
                            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
                            fg=COLORS.get("button_fg", "#FFFFFF"),
                        )
                    except Exception:
                        pass
        except Exception:
            pass

        self.results_panel.config(
            bg=bg_main,
            bd=0,
            relief="flat",
            highlightthickness=2,
            highlightbackground=border_color,
            highlightcolor=border_color,
        )
        if self.high_contrast:
            # Adjust panels for high-contrast theme
            self.results_label.config(bg=COLORS["contrast_panel_bg"], fg=fg_panel)
            self.total_label.config(bg=COLORS["contrast_panel_bg"], fg=fg_panel)
            self.footer.config(bg=COLORS["contrast_panel_bg"])
            # Make footer copyright text high-contrast as well
            try:
                self.footer_label.config(
                    bg=COLORS["contrast_panel_bg"],
                    fg=COLORS.get("contrast_fg", "#FFFF00"),
                )
            except Exception:
                pass
            # Ensure any branding/logo is visible in high-contrast
            try:
                # Compute a reasonable size based on current main content.
                w = max(2, self.main_content.winfo_width())
                h = max(2, self.main_content.winfo_height())
                side_right = max(96, int(min(w, h) * 0.60))

                # Prefer an explicitly supplied high-contrast logo, fall back
                # to the standard `logo-prosegur.png` in the icon folder.
                hc_logo_path = (
                    HIGH_CONTRAST_LOGOS.get("prosegur")
                    or ICON_PATHS.get("prosegur")
                    or os.path.join(
                        os.path.dirname(__file__), "icon", "logo-prosegur.png"
                    )
                )

                if hc_logo_path and os.path.exists(hc_logo_path):
                    with Image.open(hc_logo_path) as im:
                        img = im.convert("RGBA").resize(
                            (side_right, side_right), Image.LANCZOS
                        )
                        # Use strong alpha in high-contrast so the logo reads clearly
                        # and convert it to a white silhouette for maximum contrast.
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
                                pass
                        # Place and ensure it stays behind the webcam panel
                        try:
                            self.prosegur_globe_right_label.place(
                                relx=1.0,
                                rely=1.0,
                                anchor="se",
                                x=-48,
                                y=-(SIZES.get("footer_height", 30) + 8),
                            )
                            self.prosegur_globe_right_label.lower(self.webcam_panel)
                        except Exception:
                            pass
                else:
                    # If no file, clear the label
                    try:
                        self.prosegur_globe_right_label.config(image="")
                    except Exception:
                        pass
            except Exception:
                try:
                    self.prosegur_globe_right_label.config(image="")
                except Exception:
                    pass
        else:
            # Restore normal theme visuals
            self.results_label.config(bg=COLORS["background"], fg=fg_panel)
            self.total_label.config(bg=COLORS["background"], fg=fg_panel)
            self.footer.config(bg=COLORS["footer_bg"])
            # Restore footer copyright color
            try:
                self.footer_label.config(
                    bg=COLORS["footer_bg"], fg=COLORS.get("footer_fg", "#000000")
                )
            except Exception:
                pass
            # Also regenerate the right-bottom globe for normal theme
            try:
                w = max(2, self.main_content.winfo_width())
                h = max(2, self.main_content.winfo_height())
                # Match the larger branding size used when rendering the logo
                side_right = max(96, int(min(w, h) * 0.60))
                globe_right_img = generate_globe_icon(side_right)
                self.prosegur_globe_right_photo = ImageTk.PhotoImage(globe_right_img)
                try:
                    self.prosegur_globe_right_label.config(
                        bg=COLORS["background"], image=self.prosegur_globe_right_photo
                    )
                    try:
                        self.prosegur_globe_right_label.lower(self.webcam_panel)
                    except Exception:
                        pass
                except Exception:
                    self.prosegur_globe_right_label.config(image="")
            except Exception:
                try:
                    self.prosegur_globe_right_label.config(image="")
                except Exception:
                    pass

    # Update visible strings for the current language.
    def update_language(self) -> None:

        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        self.title_label.config(text=strings.get("title", "CoinScan"))
        self.scan_btn.config(text=strings.get("scan", "Scan"))
        self.results_label.config(text=strings.get("results", "Results"))
        self.total_label.config(text=strings.get("total", "TOTAL: €0.00"))

        # Re-populate the listbox from the internal model so values are preserved
        # when the language changes. If the recognition_list hasn't been created yet
        # (e.g. called early during init), skip safely.
        if hasattr(self, "recognition_list") and hasattr(self, "detected_coins"):
            self.update_recognition_list()

    # Resize the main window to fit chosen webcam size (unless fullscreen).
    def resize_window_for_webcam(self) -> None:

        if getattr(self, "fullscreen", False):
            return

        self.update_idletasks()

        results_w = max(self.results_panel.winfo_reqwidth(), 320)
        width = SIZES["sidebar_width"] + 40 + self.current_size[0] + 40 + results_w + 40
        height = max(700, self.current_size[1] + 40 + 40 + 48 + SIZES["footer_height"])

        self.geometry(f"{width}x{height}")

    # Start the recognition process (delegates to webcam_stream).
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

    def handle_recognition_results(self, results: list) -> None:
        """Receive structured detection results from webcam_stream.

        results: list of tuples (value, label, colour_label, radius, mean_hue)
        This runs on the Tk main thread.
        """
        try:
            # Parse incoming results into normalized dicts
            new_coins = [
                {
                    "value": float(r[0]),
                    "label": str(r[1]),
                    "colour": str(r[2]),
                    "radius": int(r[3]),
                    "hue": float(r[4]),
                }
                for r in results
            ]
        except Exception:
            new_coins = []

        # Append new detections to the existing list so rescans accumulate.
        # Avoid exact-duplicate entries to reduce accidental double-counting.
        try:
            for coin in new_coins:
                if coin not in self.detected_coins:
                    self.detected_coins.append(coin)
        except Exception:
            # Fallback: if appending fails, replace the list to keep UI consistent
            self.detected_coins = new_coins

        # Update UI list and totals
        self.update_recognition_list()

    # Show About dialog with version and description.
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

    # Show (placeholder) settings dialog.
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

    # Confirm exit with the user and quit if accepted.
    def confirm_exit(self) -> None:
        confirm_text = LANGUAGES.get(self.current_lang, LANGUAGES["en"]).get(
            "exit_confirm", "Are you sure you want to exit CoinScan?"
        )
        if messagebox.askokcancel("Exit", confirm_text):
            self.quit()

    # Reset UI to initial state.
    def go_home(self) -> None:
        self.recognition_list.delete(0, "end")
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        self.total_label.config(text=strings.get("total", "TOTAL: €0.00"))
        self.webcam_label.config(image="")

    # Set fullscreen state (attempt native fullscreen, fallback to maximized).
    def set_fullscreen(self, enable: bool = True) -> None:

        self.fullscreen = bool(enable)
        try:
            self.attributes("-fullscreen", self.fullscreen)
        except Exception:

            self.state("zoomed" if self.fullscreen else "normal")

    # Toggle fullscreen mode.
    def toggle_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(not self.fullscreen)

    # Exit fullscreen mode.
    def exit_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(False)

    # Add a new coin entry (show a dialog to enter details).
    def add_coin(self) -> None:

        dlg = CoinEditDialog(self)
        result = dlg.show()

        if result and isinstance(result, dict):
            # Ensure value is float
            try:
                result["value"] = float(result["value"])
            except ValueError:
                result["value"] = 0.0

            # Add to internal model
            self.detected_coins.append(result)

            # Update recognition list display
            self.update_recognition_list()

    # Edit the currently selected coin entry in the list.
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
                # Ensure value is float
                try:
                    result["value"] = float(result["value"])
                except ValueError:
                    result["value"] = 0.0

                # Update internal model
                self.detected_coins[index] = result

                # Update recognition list display
                self.update_recognition_list()
        except Exception:
            pass

    # Remove the currently selected coin entry from the list.
    def remove_selected(self) -> None:
        try:
            selection = self.recognition_list.curselection()
            if not selection:
                return

            index = selection[0]

            # Remove from internal model
            del self.detected_coins[index]

            # Update recognition list display
            self.update_recognition_list()
        except Exception:
            pass

    def get_total_value(self) -> float:
        """Return the total value of detected coins as a float.
        Convert each entry safely and ignore invalid values instead of failing
        the whole sum.
        """
        total = 0.0
        for coin in getattr(self, "detected_coins", []):
            v = coin.get("value", 0)
            try:
                total += float(v)
            except Exception:
                # ignore malformed / non-numeric entries
                continue
        return total

    def show_total(self) -> None:
        """Display the total value in a message box."""
        total = self.get_total_value()
        messagebox.showinfo("Total", f"TOTAL: €{total:.2f}", parent=self)

    def update_recognition_list(self) -> None:
        try:
            self.recognition_list.delete(0, "end")

            # Add all detected coins to the listbox, format values safely
            for coin in self.detected_coins:
                try:
                    value = float(coin.get("value", 0))
                except Exception:
                    value = 0.0
                label = f"{coin.get('label', '')} ({value:.2f} €)"
                self.recognition_list.insert("end", label)

            # Update total label using the centralized accessor
            total_value = self.get_total_value()
            self.total_label.config(text=f"TOTAL: €{total_value:.2f}")
        except Exception:
            pass


# Dialog for adding/editing a coin entry.
class CoinEditDialog:
    def __init__(self, parent: tk.Toplevel, coin: Optional[dict] = None) -> None:
        self.parent = parent
        self.coin = coin

        # Dialog window
        self.win = tk.Toplevel(parent)
        self.win.title("Edit Coin Entry")
        self.win.configure(bg=COLORS["background"])
        self.win.transient(parent)
        self.win.grab_set()

        # Coin details form
        self.form_frame = tk.Frame(self.win, bg=COLORS["background"])
        self.form_frame.pack(padx=20, pady=20, fill="x")

        tk.Label(
            self.form_frame,
            text="Value (in €):",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.value_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 10),
            fg="#000000",
            bd=1,
            relief="solid",
        )
        self.value_entry.grid(row=0, column=1, pady=(0, 10))

        tk.Label(
            self.form_frame,
            text="Label:",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.label_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 10),
            fg="#000000",
            bd=1,
            relief="solid",
        )
        self.label_entry.grid(row=1, column=1, pady=(0, 10))

        tk.Label(
            self.form_frame,
            text="Color:",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))

        self.color_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 10),
            fg="#000000",
            bd=1,
            relief="solid",
        )
        self.color_entry.grid(row=2, column=1, pady=(0, 10))

        tk.Label(
            self.form_frame,
            text="Radius:",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=3, column=0, sticky="w", pady=(0, 10))

        self.radius_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 10),
            fg="#000000",
            bd=1,
            relief="solid",
        )
        self.radius_entry.grid(row=3, column=1, pady=(0, 10))

        tk.Label(
            self.form_frame,
            text="Hue:",
            bg=COLORS["background"],
            fg="#000000",
            font=("Segoe UI", 10),
        ).grid(row=4, column=0, sticky="w", pady=(0, 10))

        self.hue_entry = tk.Entry(
            self.form_frame,
            font=("Segoe UI", 10),
            fg="#000000",
            bd=1,
            relief="solid",
        )
        self.hue_entry.grid(row=4, column=1, pady=(0, 10))

        # Buttons
        self.button_frame = tk.Frame(self.win, bg=COLORS["background"])
        self.button_frame.pack(pady=(10, 0))

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
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=20,
            pady=8,
        ).pack(side="left", padx=10)

        tk.Button(
            self.button_frame,
            text="Cancel",
            command=self.on_cancel,
            font=FONTS["button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            bd=0,
            padx=20,
            pady=8,
        ).pack(side="left", padx=10)

        # Fill in current coin details if editing
        if coin:
            self.value_entry.insert(0, str(coin.get("value", "")))
            self.label_entry.insert(0, coin.get("label", ""))
            self.color_entry.insert(0, coin.get("colour", ""))
            self.radius_entry.insert(0, str(coin.get("radius", "")))
            self.hue_entry.insert(0, str(coin.get("hue", "")))

        self.win.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.value_entry.focus_set()

    # Show the dialog and return the result.
    def show(self) -> Optional[dict]:
        self.win.deiconify()
        self.parent.wait_window(self.win)
        return getattr(self, "result", None)

    # Handle OK button press: validate and save the coin data.
    def on_ok(self) -> None:
        try:
            value = float(self.value_entry.get())
            label = self.label_entry.get()
            colour = self.color_entry.get()
            radius = float(self.radius_entry.get())
            hue = float(self.hue_entry.get())

            self.result = {
                "value": value,
                "label": label,
                "colour": colour,
                "radius": radius,
                "hue": hue,
            }

            self.win.destroy()
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Please enter valid values for all fields.",
                parent=self.win,
            )

    # Handle Cancel button press: do not save any data.
    def on_cancel(self) -> None:
        self.win.destroy()


if __name__ == "__main__":

    app = CoinScanApp()
    app.mainloop()


def sum_detected_coins(detected_coins: list[dict]) -> float:
    total = 0.0
    for coin in detected_coins:
        try:
            total += float(coin.get("value", 0))
        except Exception:
            continue
    return total