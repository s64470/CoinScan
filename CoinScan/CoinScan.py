# -*- coding: utf-8 -*-
# Main file for the CoinScan GUI

import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
from ui_config import (
    UI_FONT_PARAMS,
    TITLE_FONT_PARAMS,
    MONO_FONT_PARAMS,
    BUTTON_STYLE_PARAMS,
    on_enter,
    on_leave,
)
from language import LANGUAGES, switch_language
from webcam_stream import update_recognition
from tkinter import messagebox

# Global state variables
current_size = (320, 240)
current_lang = "de"
high_contrast = False


def change_font_size(delta):
    """Change the font size for all fonts."""
    min_size, max_size = 8, 32
    for font in [UI_FONT, TITLE_FONT, MONO_FONT]:
        new_size = max(min_size, min(max_size, font.cget("size") + delta))
        font.configure(size=new_size)


def set_current_lang(lang):
    """Set the global language variable."""
    global current_lang
    current_lang = lang


def toggle_size(scan_button, size_button):
    """Toggle webcam resolution and update the size button text."""
    global current_size
    strings = LANGUAGES[current_lang]
    if scan_button["state"] == "disabled":
        return
    if current_size == (320, 240):
        current_size = (640, 480)
        size_button.config(text=strings["size_minus"])
    else:
        current_size = (320, 240)
        size_button.config(text=strings["size_plus"])


def exit_program(root):
    """Show a confirmation dialog and exit if confirmed."""
    strings = LANGUAGES[current_lang]
    if messagebox.askyesno(strings["exit_dialog_title"], strings["exit_dialog_text"]):
        root.destroy()


def show_help():
    """Show the help dialog in the current language."""
    strings = LANGUAGES[current_lang]
    messagebox.showinfo(strings["help_dialog_title"], strings["help_dialog_text"])


def show_about():
    """Show the About dialog in the current language."""
    strings = LANGUAGES[current_lang]
    messagebox.showinfo(strings["about_title"], strings["about_text"])


def center_windowframe(root):
    """Center the main window on the screen."""
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def toggle_contrast():
    """Toggle between default and high-contrast (accessible) themes."""
    global high_contrast
    high_contrast = not high_contrast
    if high_contrast:
        bg_color = "black"
        fg_color = "yellow"
        btn_bg = "#333"
        btn_fg = "white"
        entry_bg = "black"
        entry_fg = "yellow"
    else:
        bg_color = "white"
        fg_color = "black"
        btn_bg = BUTTON_STYLE["bg"]
        btn_fg = BUTTON_STYLE["fg"]
        entry_bg = "white"
        entry_fg = "black"
    sidebar.config(bg=bg_color)
    for widget in sidebar.winfo_children():
        widget.config(bg=btn_bg, fg=btn_fg)
    content.config(bg=bg_color)
    widgets["title"].config(bg=bg_color, fg=fg_color)
    widgets["total_label"].config(bg=bg_color, fg=fg_color)
    widgets["recognition"].config(bg=entry_bg, fg=entry_fg)
    widgets["scan_button"].config(bg=btn_bg, fg=btn_fg)
    widgets["size_button"].config(bg=btn_bg, fg=btn_fg)
    contrast_button.config(bg=btn_bg, fg=btn_fg)
    try:
        menu_bar.config(bg=bg_color, fg=fg_color)
    except Exception:
        pass


def main():
    """Build and run the GUI."""
    global current_lang, current_size, sidebar, content, widgets, menu_bar, contrast_button
    root = tk.Tk()
    root.title("CoinScan")
    root.geometry("500x500")

    # Create Font objects after root exists
    global UI_FONT, TITLE_FONT, MONO_FONT, BUTTON_STYLE
    UI_FONT = tkFont.Font(root=root, **UI_FONT_PARAMS)
    TITLE_FONT = tkFont.Font(root=root, **TITLE_FONT_PARAMS)
    MONO_FONT = tkFont.Font(root=root, **MONO_FONT_PARAMS)
    BUTTON_STYLE = dict(BUTTON_STYLE_PARAMS)
    BUTTON_STYLE["font"] = UI_FONT

    # --- Sidebar ---
    sidebar = tk.Frame(root, bg="#2c3e50", width=60)
    sidebar.pack(side="left", fill="y")

    # Sidebar icon buttons (navigation/settings)
    for icon in ["🏠", "⚙️", "⬇️"]:
        btn = tk.Button(
            sidebar, text=icon, bg="#2c3e50", fg="white", relief="flat", font=UI_FONT
        )
        btn.pack(pady=10)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Font size adjustment buttons (A+/A-)
    font_increase_btn = tk.Button(
        sidebar, text="A+", command=lambda: change_font_size(1), font=UI_FONT
    )
    font_decrease_btn = tk.Button(
        sidebar, text="A-", command=lambda: change_font_size(-1), font=UI_FONT
    )
    font_increase_btn.pack(pady=5)
    font_decrease_btn.pack(pady=5)

    # Contrast toggle button with icon
    contrast_icon_img = Image.open("flagicon/contrast_icon.png").resize((24, 24))
    contrast_icon = ImageTk.PhotoImage(contrast_icon_img)
    contrast_button = tk.Button(
        sidebar,
        image=contrast_icon,
        command=toggle_contrast,
        bg=BUTTON_STYLE["bg"],
        fg=BUTTON_STYLE["fg"],
        activebackground=BUTTON_STYLE["activebackground"],
        activeforeground=BUTTON_STYLE["activeforeground"],
        relief=BUTTON_STYLE["relief"],
        bd=BUTTON_STYLE["bd"],
        padx=BUTTON_STYLE["padx"],
        pady=BUTTON_STYLE["pady"],
    )
    contrast_button.image = contrast_icon
    contrast_button.pack(pady=10)
    contrast_button.bind("<Enter>", on_enter)
    contrast_button.bind("<Leave>", on_leave)

    # Main content area
    content = tk.Frame(root, bg="white")
    content.pack(side="right", expand=True, fill="both")

    # Language selection buttons (flags)
    lang_frame = tk.Frame(content, bg="white")
    lang_frame.pack(pady=5)
    flag_images = {
        "de": ImageTk.PhotoImage(Image.open("flagicon/flag_DE.png").resize((24, 24))),
        "en": ImageTk.PhotoImage(Image.open("flagicon/flag_UK.png").resize((24, 24))),
    }
    widgets = {}

    # Menu bar setup
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(
        label=LANGUAGES[current_lang]["exit"], command=lambda: exit_program(root)
    )
    menu_bar.add_cascade(
        label=LANGUAGES[current_lang].get("file", "File"), menu=file_menu
    )
    widgets["menu_bar"] = menu_bar
    widgets["file_menu"] = file_menu
    widgets["file_menu_exit_index"] = 0

    help_icon_img = Image.open("flagicon/help_icon.png").resize((16, 16))
    help_icon = ImageTk.PhotoImage(help_icon_img)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label=LANGUAGES[current_lang]["help"],
        command=show_help,
        image=help_icon,
        compound="left",
    )
    help_menu.add_separator()
    help_menu.add_command(
        label=LANGUAGES[current_lang]["about_title"],
        command=show_about,
    )
    menu_bar.add_cascade(label=LANGUAGES[current_lang]["help"], menu=help_menu)
    widgets["help_menu"] = help_menu
    widgets["help_menu_index"] = 0
    widgets["help_icon"] = help_icon

    # Settings menu
    settings_menu = tk.Menu(menu_bar, tearoff=0)
    settings_menu.add_command(label="High Contrast Mode", command=toggle_contrast)
    settings_menu.add_separator()
    settings_menu.add_command(
        label="Increase Font Size (A+)", command=lambda: change_font_size(1)
    )
    settings_menu.add_command(
        label="Decrease Font Size (A-)", command=lambda: change_font_size(-1)
    )
    menu_bar.add_cascade(label="Settings", menu=settings_menu)

    # Language flag buttons for switching UI language
    for code in ["de", "en"]:
        lang_btn = tk.Button(
            lang_frame,
            image=flag_images[code],
            command=lambda c=code: [
                set_current_lang(c),
                switch_language(c, widgets, current_size),
            ],
            **BUTTON_STYLE,
        )
        lang_btn.image = flag_images[code]
        lang_btn.pack(side="left", padx=5)
        lang_btn.bind("<Enter>", on_enter)
        lang_btn.bind("<Leave>", on_leave)

    # Main title label
    widgets["title"] = tk.Label(
        content, text=LANGUAGES[current_lang]["title"], font=TITLE_FONT, bg="white"
    )
    widgets["title"].pack(pady=10)

    # Webcam display row (webcam image + size toggle button)
    webcam_row = tk.Frame(content, bg="white")
    webcam_row.pack(pady=5)
    widgets["webcam_label"] = tk.Label(webcam_row, bg="black")
    widgets["webcam_label"].pack(side="left", padx=5)
    widgets["size_button"] = tk.Button(
        webcam_row,
        text=LANGUAGES[current_lang]["size_plus"],
        command=lambda: toggle_size(widgets["scan_button"], widgets["size_button"]),
        **BUTTON_STYLE,
    )
    widgets["size_button"].pack(side="left", padx=5)
    widgets["size_button"].bind("<Enter>", on_enter)
    widgets["size_button"].bind("<Leave>", on_leave)

    # Listbox to display recognized coins
    widgets["recognition"] = tk.Listbox(content, font=MONO_FONT, height=5)
    widgets["recognition"].pack(pady=5)

    # Label to display the total value of recognized coins
    widgets["total_label"] = tk.Label(
        content, text=LANGUAGES[current_lang]["total"], font=UI_FONT, bg="white"
    )
    widgets["total_label"].pack(pady=10)

    # Scan button to start coin recognition
    button_frame = tk.Frame(content, bg="white")
    button_frame.pack(pady=10)
    widgets["scan_button"] = tk.Button(
        button_frame,
        text=LANGUAGES[current_lang]["scan"],
        command=lambda: update_recognition(
            widgets["scan_button"],
            widgets["recognition"],
            widgets["total_label"],
            widgets["webcam_label"],
            current_size,
            current_lang,
        ),
        **BUTTON_STYLE,
    )
    widgets["scan_button"].pack(side="left", padx=5)
    widgets["scan_button"].bind("<Enter>", on_enter)
    widgets["scan_button"].bind("<Leave>", on_leave)

    # Center the window on the screen
    center_windowframe(root)

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()