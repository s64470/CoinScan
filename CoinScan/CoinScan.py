import tkinter as tk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
from webcam_stream import update_recognition
from language import LANGUAGES
from ui_config import COLORS, FONTS, ICON_PATHS, SIZES, SIDEBAR_ICONS, CONTRAST_ICONS

VERSION = "1.0.0"
ABOUT_TEXT = (
    "CoinScan is a desktop application designed to help users quickly identify and count Euro coins using their computer’s webcam.\n\n"
    "Key Features:\n"
    "- Live coin scanning and recognition via webcam\n"
    "- Automatic detection of coin type and value\n"
    "- Multilingual interface (English & German)\n"
    "- High-contrast mode for improved accessibility\n"
    "- Simple, intuitive design\n\n"
    "How it works:\n"
    "Place your coins in view of your webcam and click “Scan Coins.” CoinScan will detect coins in the centre of the image, classify them by colour and size, and display the total value.\n\n"
    # "Developed for anyone who wants a fast, easy way to count coins—whether for personal use, small businesses, or educational purposes."
)


def get_flag_img(path):
    try:
        img = Image.open(path).resize(SIZES["flag"])
    except Exception:
        img = Image.new("RGB", SIZES["flag"], "grey")
    return ImageTk.PhotoImage(img)


class CoinScanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_lang = "en"
        self.current_size = SIZES["webcam_large"]
        self.high_contrast = False
        self.title(f"CoinScan v{VERSION}")
        self.geometry(f"{SIZES['window'][0]}x{SIZES['window'][1]}")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(dim) for dim in self.geometry().split("+")[0].split("x"))
        x = (screen_width // 2) - (size[0] // 2)
        y = (screen_height // 2) - (size[1] // 2)
        self.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.create_widgets()
        self.update_language()
        self.apply_contrast()

    def create_widgets(self):
        # Top bar
        top_bar = tk.Frame(self, bg=COLORS["topbar_bg"], height=48)
        top_bar.pack(side="top", fill="x")

        # Logo (left side)
        try:
            self.logo_img = Image.open("icon/logo.png").resize(
                (SIZES["logo_width"], SIZES["logo_width"])
            )
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
        except Exception:
            self.logo_photo = None
        if self.logo_photo:
            self.logo_label = tk.Label(
                top_bar, image=self.logo_photo, bg=COLORS["topbar_bg"]
            )
            self.logo_label.pack(side="left", padx=(0, 0))  # Flush to window border

        self.title_label = tk.Label(
            top_bar, font=FONTS["title"], bg=COLORS["topbar_bg"]
        )
        self.title_label.pack(side="left", padx=20)

        # Top bar right controls (language flags and contrast)
        topbar_controls = tk.Frame(top_bar, bg=COLORS["topbar_bg"])
        topbar_controls.pack(side="right", padx=10)
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
        tk.Frame(topbar_controls, width=16, bg=COLORS["topbar_bg"]).pack(side="left")
        self.contrast_btn = tk.Button(
            topbar_controls,
            text=CONTRAST_ICONS["normal"],
            bd=0,
            bg=COLORS["topbar_bg"],
            command=self.toggle_contrast,
            font=FONTS["button"],
        )
        self.contrast_btn.pack(side="left", padx=8)

        # Sidebar (width always matches logo width)
        self.sidebar = tk.Frame(
            self, bg=COLORS["sidebar_bg"], width=SIZES["sidebar_width"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar_buttons = []
        # Sidebar navigation buttons (except Exit)
        for idx, icon in enumerate(SIDEBAR_ICONS):
            if idx == 3:
                continue  # Skip Exit button here
            if idx == 0:
                btn = tk.Button(
                    self.sidebar,
                    text=icon,
                    font=FONTS["sidebar"],
                    bg=COLORS["sidebar_bg"],
                    fg=COLORS["sidebar_fg"],
                    bd=0,
                    relief="flat",
                    command=self.go_home,
                )
            elif idx == 1:
                btn = tk.Button(
                    self.sidebar,
                    text=icon,
                    font=FONTS["sidebar"],
                    bg=COLORS["sidebar_bg"],
                    fg=COLORS["sidebar_fg"],
                    bd=0,
                    relief="flat",
                    command=self.show_settings,
                )
            elif idx == 2:
                btn = tk.Button(
                    self.sidebar,
                    text=icon,
                    font=FONTS["sidebar"],
                    bg=COLORS["sidebar_bg"],
                    fg=COLORS["sidebar_fg"],
                    bd=0,
                    relief="flat",
                    command=self.show_about,
                )
            btn.pack(pady=20)
            self.sidebar_buttons.append(btn)
        # Exit button under sidebar
        exit_btn = tk.Button(
            self.sidebar,
            text=SIDEBAR_ICONS[3],  # Exit icon
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
        main_content = tk.Frame(self, bg=COLORS["background"])
        main_content.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        # Webcam panel (left)
        self.webcam_panel = tk.Frame(
            main_content, bg=COLORS["panel_bg"], bd=2, relief="groove"
        )
        self.webcam_panel.pack(side="left", padx=40, pady=40, fill="both", expand=True)
        self.webcam_label = tk.Label(self.webcam_panel, bg="black", width=80, height=24)
        self.webcam_label.pack(pady=10)
        self.recognition_list = tk.Listbox(
            self.webcam_panel, font=FONTS["listbox"], height=5, width=50
        )
        self.recognition_list.pack(pady=10)
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
        # Size buttons
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
        self.size_btn_large = tk.Button(
            size_frame,
            text="800x600",
            font=FONTS["size_button"],
            bg=COLORS["button_bg"],
            fg=COLORS["button_fg"],
            activebackground=COLORS["button_active_bg"],
            activeforeground=COLORS["button_active_fg"],
            relief="raised",
            bd=0,
            padx=10,
            pady=5,
            command=lambda: self.set_size(SIZES["webcam_large"]),
        )
        self.size_btn_large.pack(side="left", padx=5)
        self.set_size(self.current_size)

        # Results panel (right)
        self.results_panel = tk.Frame(
            main_content, bg=COLORS["topbar_bg"], bd=2, relief="ridge"
        )
        self.results_panel.pack(side="right", padx=40, pady=40, fill="y")
        # Results label
        self.results_label = tk.Label(
            self.results_panel, font=FONTS["results"], bg=COLORS["topbar_bg"]
        )
        self.results_label.pack(pady=(20, 10))
        # Total label
        self.total_label = tk.Label(
            self.results_panel,
            font=FONTS["total"],
            bg=COLORS["topbar_bg"],
            fg=COLORS["results_fg"],
        )
        self.total_label.pack(pady=(0, 10))

        # Footer (left-aligned copyright)
        self.footer = tk.Frame(
            self, bg=COLORS["topbar_bg"], height=SIZES["footer_height"]
        )
        self.footer.pack(side="bottom", fill="x")
        self.footer_label = tk.Label(
            self.footer,
            text="© 2025 Your Name or Organisation. All rights reserved.",
            font=FONTS["footer"],
            bg=COLORS["topbar_bg"],
            fg=COLORS["sidebar_bg"],
            anchor="w",
            justify="left",
        )
        self.footer_label.pack(padx=16, pady=8, side="left")

    def set_language(self, lang):
        self.current_lang = lang
        self.update_language()
        self.apply_contrast()

    def update_language(self):
        strings = LANGUAGES[self.current_lang]
        self.title_label.config(text=strings["title"])
        self.scan_btn.config(text=strings["scan"])
        self.results_label.config(text=strings["results"])
        self.total_label.config(text=strings["total"])
        self.recognition_list.delete(0, "end")

    def set_size(self, size):
        self.current_size = size
        if size == SIZES["webcam_small"]:
            self.size_btn_small.config(relief="sunken")
            self.size_btn_large.config(relief="raised")
        else:
            self.size_btn_small.config(relief="raised")
            self.size_btn_large.config(relief="sunken")

    def toggle_contrast(self):
        self.high_contrast = not self.high_contrast
        self.apply_contrast()

    def apply_contrast(self):
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
        self.configure(bg=bg_main)
        self.title_label.config(bg=bg_panel, fg=fg_panel)
        self.contrast_btn.config(bg=bg_panel, fg=fg_panel, text=contrast_icon)
        self.sidebar.config(bg=sidebar_bg)
        for btn in self.sidebar_buttons:
            btn.config(bg=sidebar_bg, fg=sidebar_fg)
        # Removed version label update
        self.webcam_panel.config(bg=bg_panel)
        self.webcam_label.config(bg=entry_bg, fg=entry_fg)
        self.recognition_list.config(bg=entry_bg, fg=entry_fg)
        self.scan_btn.config(
            bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg
        )
        self.size_btn_small.config(
            bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg
        )
        self.size_btn_large.config(
            bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg
        )
        self.results_panel.config(bg=bg_panel)
        self.results_label.config(bg=bg_panel, fg=fg_panel)
        self.total_label.config(bg=bg_panel, fg=fg_panel)
        self.footer.config(bg=bg_panel)
        self.footer_label.config(bg=bg_panel, fg=sidebar_bg)

    def start_recognition(self):
        update_recognition(
            self.scan_btn,
            self.recognition_list,
            self.total_label,
            self.webcam_label,
            self.current_size,
            self.current_lang,
        )

    def show_about(self):
        about_win = tk.Toplevel(self)
        about_win.title("About CoinScan")
        about_win.resizable(False, False)
        about_win.configure(bg=COLORS["background"])
        tk.Label(
            about_win,
            text="About CoinScan",
            font=FONTS["about_title"],
            bg=COLORS["background"],
        ).pack(padx=20, pady=(20, 10))
        tk.Message(
            about_win,
            text=ABOUT_TEXT,
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
        confirm_text = LANGUAGES[self.current_lang].get(
            "exit_confirm", "Are you sure you want to exit CoinScan?"
        )
        if messagebox.askokcancel("Exit", confirm_text):
            self.quit()

    def go_home(self):
        self.recognition_list.delete(0, "end")
        self.total_label.config(text=LANGUAGES[self.current_lang]["total"])
        self.webcam_label.config(image="")


if __name__ == "__main__":
    app = CoinScanApp()
    app.mainloop()