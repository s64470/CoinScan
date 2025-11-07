import os
import tkinter as tk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk, ImageDraw

# Import recognition entry point and UI resources
from webcam_stream import update_recognition
from language import LANGUAGES
from ui_config import (
    COLORS,
    FONTS,
    ICON_PATHS,
    SIZES,
    SIDEBAR_ICONS,
    CONTRAST_ICONS,
)

VERSION = "1.0.0"

# Localized About texts (kept as constants for easy editing/localization)
ABOUT_TEXTS = {
    "en": (
        "CoinScan is a desktop application designed to help users quickly identify and count Euro coins using their computer’s webcam.\n\n"
        "Key Features:\n"
        "- Live coin scanning and recognition via webcam\n"
        "- Automatic detection of coin type and value\n"
        "- Multilingual interface (English & German)\n"
        "- High-contrast mode for improved accessibility\n"
        "- Simple, intuitive design\n\n"
        "How it works:\n"
        "Place your coins in view of your webcam and click “Scan Coins.” CoinScan will detect coins in the centre of the image, classify them by colour and size, and display the total value.\n\n"
    ),
    "de": (
        "CoinScan ist eine Desktop-Anwendung, mit der Sie Euro-Münzen schnell mithilfe der Webcam Ihres Computers erkennen und zählen können.\n\n"
        "Hauptfunktionen:\n"
        "- Live-Erkennung und -Erfassung von Münzen über die Webcam\n"
        "- Automatische Bestimmung von Münztyp und -wert\n"
        "- Mehrsprachige Oberfläche (Englisch & Deutsch)\n"
        "- Hochkontrastmodus für bessere Barrierefreiheit\n"
        "- Einfache, intuitive Bedienung\n\n"
        "So funktioniert’s:\n"
        "Legen Sie Ihre Münzen in den Sichtbereich der Webcam und klicken Sie auf „Münzen scannen“. CoinScan erkennt die Münzen im Bildzentrum, klassifiziert sie nach Farbe und Größe und zeigt den Gesamtwert an.\n\n"
    ),
}


def get_flag_img(path):
    """
    Load and return a Tk-compatible PhotoImage for a flag icon.

    - Builds an absolute path relative to this script (robust to varying CWDs).
    - Returns a placeholder grey image if loading fails.
    """
    base = os.path.dirname(__file__)
    full_path = os.path.join(base, path)
    try:
        img = Image.open(full_path).resize(SIZES["flag"])
    except Exception:
        # Fallback: create a plain grey image so UI remains usable even if resource missing
        img = Image.new("RGB", SIZES["flag"], "grey")
    return ImageTk.PhotoImage(img)


def load_logo_photo() -> ImageTk.PhotoImage | None:
    """
    Try to load `icon/logo-prosegur.png` and return a PhotoImage.
    Fallback order:
      - PNG at `icon/logo-prosegur.png`
      - Generated placeholder bitmap
    Returns None only if everything fails.
    """
    base = os.path.dirname(__file__)
    size = (SIZES["logo_width"], SIZES["logo_width"])
    png_path = os.path.join(base, "icon", "logo-prosegur.png")

    # PNG preferred
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass

    # Generated placeholder (simple black circle with P)
    try:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = size[0] // 2 - 2
        cx = cy = size[0] // 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#000000")
        # Minimalistic P
        d.rectangle((cx - r // 3, cy - r // 2, cx - r // 6, cy + r // 2), fill="#FFD100")
        d.ellipse((cx - r // 6, cy - r // 3, cx + r // 2, cy + r // 3), outline="#FFD100", width=3)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def generate_prosegur_globe_bg(width: int, height: int) -> Image.Image:
    """
    Generate a corporate-style Prosegur background with exactly ONE globe watermark:
    - Base corporate yellow (#FFD100).
    - Single faded globe (centered) with latitude/longitude lines.
    """
    bg_color = COLORS.get("background", "#FFD100")
    width = max(64, int(width))
    height = max(64, int(height))

    base = Image.new("RGB", (width, height), bg_color)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    def draw_globe(cx, cy, radius, stroke_alpha=65, stroke_width=4):
        stroke = (0, 0, 0, stroke_alpha)
        # Outer circle
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=stroke, width=stroke_width)
        # Longitudes (vertical + two offsets)
        for offset in (-0.45, 0, 0.45):
            ox = int(radius * offset)
            draw.ellipse((cx - ox - radius, cy - radius, cx - ox + radius, cy + radius), outline=stroke, width=1)
        # Latitudes (three horizontal arcs)
        for frac in (-0.5, 0, 0.5):
            ry = int(radius * (0.65 + 0.25 * frac))
            draw.ellipse((cx - radius, cy - ry, cx + radius, cy + ry), outline=stroke, width=1)
        # Equator emphasized
        draw.line([(cx - radius, cy), (cx + radius, cy)], fill=stroke, width=2)

    # Single centered globe watermark
    globe_radius = int(min(width, height) * 0.32)
    draw_globe(width // 2, height // 2, globe_radius)

    base = base.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


class CoinScanApp(tk.Tk):
    """
    Main application window.

    Responsibilities:
    - Build and layout all UI widgets
    - Apply theme / contrast and font adjustments
    - Route user actions to backend functions (start_recognition -> webcam_stream.update_recognition)
    """

    def __init__(self):
        super().__init__()

        # UI state
        self.current_lang = "en"  # active language key from language.LANGUAGES
        self.current_size = SIZES["webcam_small"]  # default webcam capture size (Small)
        self.high_contrast = False  # accessibility toggle
        self.fullscreen = False  # fullscreen state (F11 toggles, Esc exits)

        # Window setup
        self.title(f"CoinScan v{VERSION}")
        self.geometry(f"{SIZES['window'][0]}x{SIZES['window'][1]}")
        self.update_idletasks()  # ensure geometry() returns updated values

        # Visual configuration
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)

        # Fullscreen key bindings
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Build UI and apply initial translations and contrast
        self.create_widgets()
        self.update_language()
        self.apply_contrast()

        # Start in full screen
        self.set_fullscreen(True)

    def create_widgets(self):
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
                self.top_bar, text="PROSEGUR", font=("Segoe UI", 14, "bold"), bg=COLORS["topbar_bg"]
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
        tk.Frame(topbar_controls, width=16, bg=COLORS["topbar_bg"]).pack(side="left")

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
            text=SIDEBAR_ICONS[3],  # Exit icon / label
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
        self._bg_image = None
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
        self.webcam_panel = tk.Frame(
            self.main_content, bg=COLORS["panel_bg"], bd=2, relief="groove"
        )
        self.webcam_panel.pack(side="left", padx=40, pady=40, fill="both", expand=True)

        # Label that will display webcam frames (image updates done by webcam_stream)
        # Set background to corporate yellow (was black) for live scan area
        self.webcam_label = tk.Label(self.webcam_panel, bg=COLORS["background"], fg="#000000")
        self.webcam_label.pack(pady=10)

        # Listbox to show detection / recognition events
        self.recognition_list = tk.Listbox(
            self.webcam_panel, font=FONTS["listbox"], height=5, width=50
        )
        self.recognition_list.pack(pady=10)

        # Scan button: triggers recognition backend
        self.scan_btn = tk.Button(
            self.webcam_panel,
            font=FONTS["button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            activebackground=COLORS["button_active_bg"],
            activeforeground=COLORS["button_active_fg"],
            relief="raised",
            bd=0,
            padx=30,
            pady=10,
            command=self.start_recognition,
        )
        self.scan_btn.pack(pady=10)

        # Size selection (only one option now)
        size_frame = tk.Frame(self.webcam_panel, bg=COLORS["panel_bg"])
        size_frame.pack(pady=5)
        self.size_btn_small = tk.Button(
            size_frame,
            text="480x360",
            font=FONTS["size_button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            activebackground=COLORS["button_active_bg"],
            activeforeground=COLORS["button_active_fg"],
            relief="raised",
            bd=0,
            padx=10,
            pady=5,
            command=lambda: self.set_size(SIZES["webcam_small"]),
        )
        self.size_btn_small.pack(side="left", padx=5)

        # Global font size controls (A- / A+)
        font_frame = tk.Frame(self.webcam_panel, bg=COLORS["panel_bg"])
        font_frame.pack(pady=(0, 10))
        tk.Label(
            font_frame,
            text="Font size:",
            bg=COLORS["panel_bg"],
            font=FONTS["button"],
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            font_frame,
            text="A-",
            font=FONTS["button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            activebackground=COLORS["button_active_bg"],
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=8,
            pady=4,
            command=lambda: self.adjust_font_size(-1),
        ).pack(side="left", padx=4)
        tk.Button(
            font_frame,
            text="A+",
            font=FONTS["button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            activebackground=COLORS["button_active_bg"],
            activeforeground=COLORS["button_active_fg"],
            bd=0,
            padx=8,
            pady=4,
            command=lambda: self.adjust_font_size(1),
        ).pack(side="left", padx=4)

        # Results panel (right side of main content)
        self.results_panel = tk.Frame(
            self.main_content, bg=COLORS["topbar_bg"], bd=2, relief="ridge"
        )
        self.results_panel.pack(side="right", padx=40, pady=40, fill="y")

        # Results label (title for results area) - text set by update_language
        self.results_label = tk.Label(
            self.results_panel, font=FONTS["results"], bg=COLORS["topbar_bg"]
        )
        self.results_label.pack(pady=(20, 10))

        # Total label shows total recognized value
        self.total_label = tk.Label(
            self.results_panel,
            font=FONTS["total"],
            bg=COLORS["topbar_bg"],
            fg=COLORS["results_fg"],
        )
        self.total_label.pack(pady=(0, 10))

        # Footer (left-aligned copyright)
        self.footer = tk.Frame(
            self, bg=COLORS["footer_bg"], height=SIZES["footer_height"]
        )
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
        self.footer_label.pack(padx=16, pady=8, side="left")

        # Initialize which size button appears selected AFTER results_panel exists
        self.set_size(self.current_size)

    def _on_main_content_resize(self, event):
        # Skip when in high-contrast mode or minimized sizes
        if getattr(self, "high_contrast", False):
            return
        self._render_background_image(max(2, event.width), max(2, event.height))

    def _render_background_image(self, width: int, height: int):
        try:
            img = generate_prosegur_globe_bg(width, height)
            self._bg_image = ImageTk.PhotoImage(img)
            self.bg_label.config(image=self._bg_image)
        except Exception:
            # If generation fails, fall back to solid background color
            self.bg_label.config(image="")

    def set_language(self, lang):
        """
        Switch the UI language and reapply any contrast rules that depend on language (if any).
        """
        self.current_lang = lang
        self.update_language()
        self.apply_contrast()

    def update_language(self):
        """
        Apply language strings to visible widgets.

        Expects LANGUAGES to be a dict mapping language keys to string dicts.
        """
        strings = LANGUAGES[self.current_lang]
        self.title_label.config(text=strings["title"])
        self.scan_btn.config(text=strings["scan"])
        self.results_label.config(text=strings["results"])
        self.total_label.config(text=strings["total"])
        # Clear the recognition list whenever language changes to avoid stale text
        self.recognition_list.delete(0, "end")

    def resize_window_for_webcam(self):
        # Skip geometry changes while in fullscreen
        if getattr(self, "fullscreen", False):
            return

        self.update_idletasks()
        # Safe to access results_panel because create_widgets creates it before set_size is called
        results_w = max(self.results_panel.winfo_reqwidth(), 320)
        width = SIZES["sidebar_width"] + 40 + self.current_size[0] + 40 + results_w + 40
        height = max(
            self.current_size[1] + 40 + 40 + 48 + SIZES["footer_height"],
            700,
        )
        # Keep current window position; only update size
        self.geometry(f"{width}x{height}")

    def set_size(self, size):
        """
        Set preferred webcam capture size and update UI state for which size button is active.
        Actual webcam resolution change happens when the recognition backend reads this value.
        """
        self.current_size = size
        self.size_btn_small.config(
            relief="sunken" if size == SIZES["webcam_small"] else "raised"
        )
        self.resize_window_for_webcam()

    def toggle_contrast(self):
        """
        Toggle high contrast mode and apply color changes.
        """
        self.high_contrast = not self.high_contrast
        self.apply_contrast()

    def adjust_font_size(self, delta):
        """
        Adjust numeric font sizes inside the shared FONTS dictionary.

        - Supports tkfont.Font instances as well as tuple/list font descriptions.
        - Ensures font size does not go below a practical minimum (6).
        - After modifying FONTS entries, this method reapplies updated fonts to visible widgets.
        """
        from tkinter import font as tkfont

        for key, f in FONTS.items():
            try:
                # If it's a tkfont.Font instance, modify it directly
                if isinstance(f, tkfont.Font):
                    current = f.cget("size")
                    f.configure(size=max(6, current + delta))
                elif isinstance(f, tuple) and len(f) >= 2 and isinstance(f[1], int):
                    # tuple like (family, size, ...)
                    new_size = max(6, f[1] + delta)
                    FONTS[key] = (f[0], new_size) + tuple(f[2:])
                elif isinstance(f, (list,)) and len(f) >= 2 and isinstance(f[1], int):
                    new_size = max(6, f[1] + delta)
                    FONTS[key] = [f[0], new_size] + f[2:]
            except Exception:
                # Robust: ignore fonts we cannot handle rather than crash the UI
                continue

        # Reapply changed fonts to widgets that use them
        self.title_label.config(font=FONTS["title"])
        self.scan_btn.config(font=FONTS["button"])
        self.size_btn_small.config(font=FONTS["size_button"])
        self.recognition_list.config(font=FONTS["listbox"])
        self.results_label.config(font=FONTS["results"])
        self.total_label.config(font=FONTS["total"])
        self.footer_label.config(font=FONTS["footer"])
        self.contrast_btn.config(font=FONTS["button"])

    def apply_contrast(self):
        """
        Apply color scheme based on the high_contrast flag.

        This swaps colors from ui_config.COLORS to high-contrast variants when needed.
        """
        if self.high_contrast:
            bg_main = COLORS["contrast_bg"]
            fg_main = COLORS["contrast_fg"]
            bg_panel = COLORS["contrast_panel_bg"]
            fg_panel = COLORS["contrast_fg"]
            btn_bg = COLORS["contrast_bg"]
            btn_fg = COLORS["contrast_fg"]
            entry_bg = COLORS["contrast_bg"]
            entry_fg = COLORS["contrast_fg"]
            sidebar_bg = COLORS["contrast_sidebar_bg"]
            sidebar_fg = COLORS["contrast_sidebar_fg"]
            contrast_icon = CONTRAST_ICONS["contrast"]
        else:
            bg_main = COLORS["background"]
            fg_main = "#000000"
            bg_panel = COLORS["panel_bg"]
            fg_panel = "#000000"
            btn_bg = COLORS["button_bg"]
            btn_fg = COLORS["button_fg"]
            entry_bg = "white"
            entry_fg = "black"
            sidebar_bg = COLORS["sidebar_bg"]
            sidebar_fg = COLORS["sidebar_fg"]
            contrast_icon = CONTRAST_ICONS["normal"]

        # Apply window and widgets colors consistently
        self.configure(bg=bg_main)
        # Keep entire top bar (logo + title + controls) corporate yellow
        if hasattr(self, "top_bar"):
            self.top_bar.config(bg=COLORS["topbar_bg"])
        self.title_label.config(bg=COLORS["topbar_bg"], fg="#000000")
        if hasattr(self, "logo_label"):
            self.logo_label.config(bg=COLORS["topbar_bg"])
        self.contrast_btn.config(bg=COLORS["topbar_bg"], fg="#000000", text=contrast_icon)
        self.sidebar.config(bg=sidebar_bg)
        for btn in self.sidebar_buttons:
            btn.config(bg=sidebar_bg, fg=sidebar_fg)
        self.webcam_panel.config(bg=bg_panel)
        if hasattr(self, "logo_label"):
            # Keep logo area on corporate yellow even in contrast mode
            self.logo_label.config(bg=COLORS["topbar_bg"])
        self.recognition_list.config(bg=entry_bg, fg=entry_fg)
        self.scan_btn.config(
            bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg
        )
        self.size_btn_small.config(
            bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg
        )
        self.results_panel.config(bg=bg_panel)
        self.results_label.config(bg=bg_panel, fg=fg_panel)
        self.total_label.config(bg=bg_panel, fg=fg_panel)

        # Footer respects corporate colors in normal mode, contrast palette in high-contrast
        if self.high_contrast:
            self.footer.config(bg=COLORS["contrast_panel_bg"])
            self.footer_label.config(bg=COLORS["contrast_panel_bg"], fg=COLORS["contrast_fg"])
        else:
            self.footer.config(bg=COLORS["footer_bg"])  # Yellow background
            self.footer_label.config(bg=COLORS["footer_bg"], fg=COLORS["footer_fg"])  # Black text

        # Background image visibility according to contrast mode
        if hasattr(self, "bg_label"):
            if self.high_contrast:
                self.bg_label.config(image="")
            else:
                # regenerate for current size
                w = max(2, self.main_content.winfo_width())
                h = max(2, self.main_content.winfo_height())
                self._render_background_image(w, h)

    def start_recognition(self):
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

    def show_about(self):
        """
        Show About dialog with app metadata and description.
        """
        about_win = tk.Toplevel(self)
        about_win.title("About CoinScan")
        about_win.resizable(False, False)
        about_win.configure(bg=COLORS["background"])
        tk.Label(
            about_win,
            text="About CoinScan",
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
            text="Close",
            command=about_win.destroy,
            font=FONTS["about_button"],
        ).pack(pady=(0, 20))

    def show_settings(self):
        """
        Show Settings dialog.

        Currently a placeholder for future settings; kept as a Toplevel for expansion.
        """
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.resizable(False, False)
        settings_win.configure(bg=COLORS["background"])
        tk.Label(
            settings_win,
            text="Settings",
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
            text="Close",
            command=settings_win.destroy,
            font=FONTS["about_button"],
        ).pack(pady=(0, 20))

    def confirm_exit(self):
        """
        Prompt the user to confirm exit using localized string if available.
        """
        confirm_text = LANGUAGES[self.current_lang].get(
            "exit_confirm", "Are you sure you want to exit CoinScan?"
        )
        if messagebox.askokcancel("Exit", confirm_text):
            self.quit()

    def go_home(self):
        """
        Reset main UI to initial state:
        - clear recognition list
        - reset total label text
        - clear webcam preview image
        """
        self.recognition_list.delete(0, "end")
        self.total_label.config(text=LANGUAGES[self.current_lang]["total"])
        # Clear any image reference in the webcam label
        self.webcam_label.config(image="")

    # ---- Fullscreen helpers ----
    def set_fullscreen(self, enable: bool = True):
        """
        Enable/disable fullscreen. Uses attribute where available, falls back to 'zoomed' state.
        """
        self.fullscreen = bool(enable)
        try:
            self.attributes("-fullscreen", self.fullscreen)
        except Exception:
            # Fallback for platforms not supporting -fullscreen
            self.state("zoomed" if self.fullscreen else "normal")

    def toggle_fullscreen(self, event=None):
        self.set_fullscreen(not self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.set_fullscreen(False)


if __name__ == "__main__":
    # Entry point for running the app directly.
    app = CoinScanApp()
    app.mainloop()