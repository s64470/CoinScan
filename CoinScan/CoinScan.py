import os
import tkinter as tk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk, ImageDraw
from typing import Optional, Callable, Tuple

# Import recognition entry point and UI resources
from webcam_stream import update_recognition
from language import LANGUAGES, ABOUT_TEXTS
from ui_config import (
    COLORS,
    FONTS,
    ICON_PATHS,
    SIZES,
    SIDEBAR_ICONS,
    CONTRAST_ICONS,
)

VERSION = "1.0.0"


def get_flag_img(path: str) -> ImageTk.PhotoImage:
    """Load and return a Tk-compatible PhotoImage for a flag icon.

    Builds an absolute path relative to this script. Returns a placeholder
    grey image if loading fails.
    """
    base = os.path.dirname(__file__)
    full_path = os.path.join(base, path)
    try:
        # Use high-quality resizing for clarity
        img = Image.open(full_path).resize(SIZES["flag"], Image.LANCZOS)
    except Exception:
        img = Image.new("RGB", SIZES["flag"], "grey")  # fallback
    return ImageTk.PhotoImage(img)


def load_logo_photo() -> Optional[ImageTk.PhotoImage]:
    """Attempt to load logo image; generate placeholder if missing."""
    base = os.path.dirname(__file__)
    size = (SIZES["logo_width"], SIZES["logo_width"])
    png_path = os.path.join(base, "icon", "logo-prosegur.png")
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path).convert("RGBA").resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass
    # Placeholder
    try:
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


def generate_prosegur_globe_bg(width: int, height: int) -> Image.Image:
    """Generate yellow background with single globe watermark bottom-right."""
    bg_color = COLORS.get("background", "#FFD100")
    width = max(64, int(width))
    height = max(64, int(height))
    base = Image.new("RGB", (width, height), bg_color)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    def draw_globe(
        cx: int, cy: int, radius: int, stroke_alpha: int = 65, stroke_width: int = 4
    ) -> None:
        stroke = (0, 0, 0, stroke_alpha)
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=stroke,
            width=stroke_width,
        )
        for offset in (-0.45, 0, 0.45):
            ox = int(radius * offset)
            draw.ellipse(
                (cx - ox - radius, cy - radius, cx - ox + radius, cy + radius),
                outline=stroke,
                width=1,
            )
        for frac in (-0.5, 0, 0.5):
            ry = int(radius * (0.65 + 0.25 * frac))
            draw.ellipse(
                (cx - radius, cy - ry, cx + radius, cy + ry), outline=stroke, width=1
            )
        draw.line([(cx - radius, cy), (cx + radius, cy)], fill=stroke, width=2)

    globe_radius = int(min(width, height) * 0.32)
    margin = max(12, globe_radius // 5)
    cx = width - globe_radius - margin
    cy = height - globe_radius - margin
    if cx - globe_radius < 0 or cy - globe_radius < 0:
        cx, cy = width // 2, height // 2
    draw_globe(cx, cy, globe_radius)
    base = base.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def generate_globe_icon(diameter: int = 40) -> Image.Image:
    diameter = max(16, int(diameter))
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = diameter // 2 - 2
    cx = cy = diameter // 2
    stroke = (0, 0, 0, 180)
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius), outline=stroke, width=3
    )
    for offset in (-0.45, 0, 0.45):
        ox = int(radius * offset)
        draw.ellipse(
            (cx - ox - radius, cy - radius, cx - ox + radius, cy + radius),
            outline=stroke,
            width=1,
        )
    for frac in (-0.5, 0, 0.5):
        ry = int(radius * (0.65 + 0.25 * frac))
        draw.ellipse(
            (cx - radius, cy - ry, cx + radius, cy + ry), outline=stroke, width=1
        )
    draw.line([(cx - radius, cy), (cx + radius, cy)], fill=stroke, width=2)
    return img


class Tooltip:
    def __init__(self, widget: tk.Widget, text_func: Callable[[], str], delay: int = 400) -> None:
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self._id: Optional[str] = None
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide_now)

    def _schedule(self, _event: tk.Event) -> None:
        self._cancel()
        self._id = self.widget.after(self.delay, self._show)

    def _cancel(self) -> None:
        if self._id is not None:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

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

    def _hide_now(self, _event: tk.Event) -> None:
        self._cancel()
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


class CoinScanApp(tk.Tk):
    """
    Main application window.

    Responsibilities:
    - Build and layout all UI widgets
    - Apply theme / contrast and font adjustments
    - Route user actions to backend functions (start_recognition -> webcam_stream.update_recognition)
    """

    def __init__(self) -> None:
        super().__init__()
        self.current_lang: str = "en"
        self.current_size: Tuple[int, int] = SIZES["webcam_small"]
        self.high_contrast: bool = False
        self.fullscreen: bool = False
        self.title(f"CoinScan v{VERSION}")
        self.geometry(f"{SIZES['window'][0]}x{SIZES['window'][1]}")
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
        """
        Construct all widgets and their layout.

        Widgets are grouped into:
        - Top bar (logo, title, language flags, contrast)
        - Sidebar (navigation & exit)
        - Main content (webcam panel and results panel)
        - Footer
        """
        # Top bar
        self.top_bar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48)
        self.top_bar.pack(side="top", fill="x")

        # Logo (left side) - load Prosegur SVG/PNG or fallback
        self.logo_photo = load_logo_photo()
        if self.logo_photo is not None:
            self.logo_label = tk.Label(
                self.top_bar, image=self.logo_photo, bg=COLORS["topbar_bg"]
            )
            self.logo_label.pack(side="left", padx=(0, 0))
        else:
            self.logo_label = tk.Label(
                self.top_bar,
                text="PROSEGUR",
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["topbar_bg"],
            )
            self.logo_label.pack(side="left", padx=(8, 0))

        # Title label (text set in update_language)
        self.title_label = tk.Label(
            self.top_bar, font=FONTS["title"], bg=COLORS["topbar_bg"]
        )
        self.title_label.pack(side="left", padx=20)

        # Top bar right controls: language flags and contrast toggle
        topbar_controls = tk.Frame(self.top_bar, bg=COLORS["topbar_bg"])
        topbar_controls.pack(side="right", padx=10)

        # Load flag images (safe loader handles missing files)
        self.flag_de = get_flag_img(ICON_PATHS["flag_de"])
        self.flag_en = get_flag_img(ICON_PATHS["flag_en"])

        # Buttons to switch languages
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

        # Spacer between language and contrast button
        tk.Frame(topbar_controls, width=32, bg=COLORS["topbar_bg"]).pack(side="left")

        # Contrast toggle button (text updated by apply_contrast)
        self.contrast_btn = tk.Button(
            topbar_controls,
            text=CONTRAST_ICONS["normal"],
            bd=0,
            bg=COLORS["topbar_bg"],
            command=self.toggle_contrast,
            font=FONTS["button"],
        )
        self.contrast_btn.pack(side="left", padx=8)

        # Sidebar (left)
        self.sidebar = tk.Frame(
            self, bg=COLORS["sidebar_bg"], width=SIZES["sidebar_width"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar_buttons = []

        # Build sidebar navigation buttons from SIDEBAR_ICONS.
        # The Exit button (index 3) is handled separately and placed at the bottom.
        for idx, icon in enumerate(SIDEBAR_ICONS):
            if idx == 3:
                continue  # Skip Exit button here

            # Map index -> action
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

        # Exit button placed at bottom of sidebar
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

        # Main content area (center)
        self.main_content = tk.Frame(self, bg=COLORS["background"])
        self.main_content.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        # Background image label for main content (globe watermark)
        self._bg_image: Optional[ImageTk.PhotoImage] = None
        self.bg_label = tk.Label(self.main_content, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()  # ensure it stays behind other widgets

        # Render initial background and update on size changes
        self.main_content.bind("<Configure>", self._on_main_content_resize)
        self._render_background_image(
            max(2, self.main_content.winfo_width()),
            max(2, self.main_content.winfo_height()),
        )

        # Webcam panel (left side of main content)
        # Make it visually transparent with a visible border
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

        # Label that will display webcam frames (image updates done by webcam_stream)
        # Set background to corporate yellow (was black) for live scan area
        self.webcam_label = tk.Label(
            self.webcam_panel, bg=COLORS["background"], fg="#000000"
        )
        self.webcam_label.pack(pady=(10, 6))

        # Primary action button centered under webcam preview
        self.scan_btn = tk.Button(
            self.webcam_panel,
            font=FONTS["button"],
            bg=COLORS.get("primary_btn_bg", COLORS["button_bg"]),
            fg=COLORS["button_fg"],
            activebackground=COLORS.get("primary_btn_hover", COLORS["button_active_bg"]),
            activeforeground=COLORS["button_active_fg"],
            relief="raised",
            bd=0,
            padx=36,
            pady=12,
            command=self.start_recognition,
        )
        self.scan_btn.pack(pady=(6, 10))

        # Font size controls (rearranged): centered pill group under Scan button
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
            activebackground=COLORS.get("primary_btn_hover", COLORS["button_active_bg"]),
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
            activebackground=COLORS.get("font_btn_inc_hover", COLORS["button_active_bg"]),
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=10,
            pady=4,
            command=lambda: self.adjust_font_size(1),
        )
        self.font_inc_btn.pack(side="left", padx=(4, 0))

        # Listbox to show detection / recognition events under the font controls
        self.recognition_list = tk.Listbox(
            self.webcam_panel, font=FONTS["listbox"], height=5, width=50
        )
        self.recognition_list.pack(pady=(0, 8))

        # Results panel (right side of main content)
        # Make it follow main background but WITH a visible border
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

        # Results label (title for results area) - text set by update_language
        self.results_label = tk.Label(
            self.results_panel, font=FONTS["results"], bg=COLORS["background"]
        )
        self.results_label.pack(pady=(20, 10))

        # Total label shows total recognized value
        self.total_label = tk.Label(
            self.results_panel,
            font=FONTS["total"],
            bg=COLORS["background"],
            fg=COLORS["results_fg"],
        )
        self.total_label.pack(pady=(0, 10))

        # Footer (left-aligned copyright)
        self.footer = tk.Frame(
            self, bg=COLORS["footer_bg"]
        )  # remove fixed height to allow globe above
        self.footer.pack(side="bottom", fill="x")

        # Globe icon above copyright label
        try:
            globe_img = generate_globe_icon(64)
            self.footer_globe_photo = ImageTk.PhotoImage(globe_img)
            self.footer_globe_label = tk.Label(
                self.footer, image=self.footer_globe_photo, bg=COLORS["footer_bg"]
            )
            # Position at bottom-right with padding
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

        # Initialize which size button appears selected AFTER results_panel exists
        self.set_size(self.current_size)
        # Initialize font buttons enabled/disabled based on current font size
        self.adjust_font_size(0)

        # Attach tooltips (after widgets creation)
        def tt(key: str) -> Callable[[], str]:
            return lambda: LANGUAGES[self.current_lang].get("tooltips", {}).get(key, "")

        Tooltip(self.scan_btn, tt("scan_btn"))
        Tooltip(self.contrast_btn, tt("contrast"))
        # Language flag buttons: need references -> find first two children of topbar_controls
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

    def _on_main_content_resize(self, event: tk.Event) -> None:
        # Skip when in high-contrast mode or minimized sizes
        if getattr(self, "high_contrast", False):
            return
        self._render_background_image(max(2, event.width), max(2, event.height))

    def _render_background_image(self, width: int, height: int) -> None:
        try:
            img = generate_prosegur_globe_bg(width, height)
            self._bg_image = ImageTk.PhotoImage(img)
            self.bg_label.config(image=self._bg_image)
        except Exception:
            self.bg_label.config(image="")

    def set_language(self, lang: str) -> None:
        """
        Switch the UI language and reapply any contrast rules that depend on language (if any).
        """
        self.current_lang = lang if lang in LANGUAGES else "en"
        self.update_language()
        self.apply_contrast()

    def update_language(self) -> None:
        """
        Apply language strings to visible widgets.

        Expects LANGUAGES to be a dict mapping language keys to string dicts.
        """
        strings = LANGUAGES.get(self.current_lang, LANGUAGES["en"])
        self.title_label.config(text=strings.get("title", "CoinScan"))
        self.scan_btn.config(text=strings.get("scan", "Scan"))
        self.results_label.config(text=strings.get("results", "Results"))
        self.total_label.config(text=strings.get("total", "TOTAL: €0.00"))
        # Clear the recognition list whenever language changes to avoid stale text
        self.recognition_list.delete(0, "end")

    def resize_window_for_webcam(self) -> None:
        # Skip geometry changes while in fullscreen
        if getattr(self, "fullscreen", False):
            return

        self.update_idletasks()
        # Safe to access results_panel because create_widgets creates it before set_size is called
        results_w = max(self.results_panel.winfo_reqwidth(), 320)
        width = SIZES["sidebar_width"] + 40 + self.current_size[0] + 40 + results_w + 40
        height = max(700, self.current_size[1] + 40 + 40 + 48 + SIZES["footer_height"])
        # Keep current window position; only update size
        self.geometry(f"{width}x{height}")

    def set_size(self, size: Tuple[int, int]) -> None:
        """
        Set preferred webcam capture size and update UI state for which size button is active.
        Actual webcam resolution change happens when the recognition backend reads this value.
        """
        self.current_size = size
        self.resize_window_for_webcam()

    def toggle_contrast(self) -> None:
        """
        Toggle high contrast mode and apply color changes.
        """
        self.high_contrast = not self.high_contrast
        self.apply_contrast()

    def adjust_font_size(self, delta: int) -> None:
        """
        Adjust numeric font sizes inside the shared FONTS dictionary.

        - Supports tkfont.Font instances as well as tuple/list font descriptions.
        - Clamps sizes to a practical range to avoid extremes.
        - After modifying FONTS entries, this method reapplies updated fonts to visible widgets.
        """
        from tkinter import font as tkfont

        MIN_SIZE = 8
        MAX_SIZE = 28

        def clamp(v: int) -> int:
            return max(MIN_SIZE, min(MAX_SIZE, int(v)))

        # Probe a representative font to determine current size (prefer button font)
        def get_current_button_size() -> int:
            f = FONTS.get("button")
            if isinstance(f, tkfont.Font):
                return int(f.cget("size"))
            if isinstance(f, (tuple, list)) and len(f) >= 2 and isinstance(f[1], int):
                return int(f[1])
            return 12

        for key, f in FONTS.items():
            try:
                if isinstance(f, tkfont.Font):
                    current = int(f.cget("size"))
                    f.configure(size=clamp(current + delta))
                elif isinstance(f, tuple) and len(f) >= 2 and isinstance(f[1], int):
                    new_size = clamp(f[1] + delta)
                    FONTS[key] = (f[0], new_size) + tuple(f[2:])
                elif isinstance(f, (list,)) and len(f) >= 2 and isinstance(f[1], int):
                    new_size = clamp(f[1] + delta)
                    FONTS[key] = [f[0], new_size] + f[2:]
            except Exception:
                continue
        # Reapply fonts
        self.title_label.config(font=FONTS["title"])
        self.scan_btn.config(font=FONTS["button"])
        self.recognition_list.config(font=FONTS["listbox"])
        self.results_label.config(font=FONTS["results"])
        self.total_label.config(font=FONTS["total"])
        self.footer_label.config(font=FONTS["footer"])
        self.contrast_btn.config(font=FONTS["button"])

        # Update inc/dec button state based on new size
        size_now = clamp(get_current_button_size())
        if hasattr(self, "font_dec_btn"):
            disabled = size_now <= MIN_SIZE
            self.font_dec_btn.config(
                state=("disabled" if disabled else "normal"),
                bg=(COLORS.get("font_btn_disabled_bg") if disabled else COLORS.get("primary_btn_bg", COLORS["button_bg"])),
                fg=(COLORS.get("font_btn_disabled_fg") if disabled else COLORS["button_fg"]),
                activebackground=COLORS.get("primary_btn_hover", COLORS["button_active_bg"]),
            )
        if hasattr(self, "font_inc_btn"):
            disabled = size_now >= MAX_SIZE
            self.font_inc_btn.config(
                state=("disabled" if disabled else "normal"),
                bg=(COLORS.get("font_btn_disabled_bg") if disabled else COLORS.get("primary_btn_bg", COLORS["button_bg"])),
                fg=(COLORS.get("font_btn_disabled_fg") if disabled else COLORS["button_fg"]),
                activebackground=COLORS.get("primary_btn_hover", COLORS["button_active_bg"]),
            )

    def apply_contrast(self) -> None:
        """Apply color scheme; ensure results_label and total_label use yellow in normal mode."""
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
        self.logo_label.config(bg=COLORS["topbar_bg"])
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
            if self.footer_globe_label:
                self.footer_globe_label.config(bg=COLORS["contrast_panel_bg"], image="")
            self.footer_label.config(
                bg=COLORS["contrast_panel_bg"], fg=COLORS["contrast_fg"]
            )
            self.bg_label.config(image="")
        else:
            self.results_label.config(bg=COLORS["background"], fg=fg_panel)
            self.total_label.config(bg=COLORS["background"], fg=fg_panel)
            self.footer.config(bg=COLORS["footer_bg"])
            if self.footer_globe_label:
                try:
                    globe_img = generate_globe_icon(64)
                    self.footer_globe_photo = ImageTk.PhotoImage(globe_img)
                    self.footer_globe_label.config(
                        bg=COLORS["footer_bg"], image=self.footer_globe_photo
                    )
                except Exception:
                    self.footer_globe_label.config(image="")
            self.footer_label.config(bg=COLORS["footer_bg"], fg=COLORS["footer_fg"])
            w = max(2, self.main_content.winfo_width())
            h = max(2, self.main_content.winfo_height())
            self._render_background_image(w, h)

    def start_recognition(self) -> None:
        """
        Trigger the recognition pipeline.

        Delegates to webcam_stream.update_recognition and passes:
        - scan button widget (so it can be disabled/label changed)
        - recognition_list Listbox (to display detections)
        - total_label (to show total value)
        - webcam_label (to display video frames)
        - current_size (preferred capture resolution)
        - current_lang (for localized recognition messages)
        """
        update_recognition(
            self.scan_btn,
            self.recognition_list,
            self.total_label,
            self.webcam_label,
            self.current_size,
            self.current_lang,
        )

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

    # ---- Fullscreen helpers ----
    def set_fullscreen(self, enable: bool = True) -> None:
        """
        Enable/disable fullscreen. Uses attribute where available, falls back to 'zoomed' state.
        """
        self.fullscreen = bool(enable)
        try:
            self.attributes("-fullscreen", self.fullscreen)
        except Exception:
            # Fallback for platforms not supporting -fullscreen
            self.state("zoomed" if self.fullscreen else "normal")

    def toggle_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(not self.fullscreen)

    def exit_fullscreen(self, event: Optional[tk.Event] = None) -> None:
        self.set_fullscreen(False)


if __name__ == "__main__":
    # Entry point for running the app directly.
    app = CoinScanApp()
    app.mainloop()