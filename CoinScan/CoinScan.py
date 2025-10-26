# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk
from ui_config import UI_FONT, TITLE_FONT, MONO_FONT, BUTTON_STYLE, on_enter, on_leave
from language import LANGUAGES, switch_language
from webcam_stream import update_recognition
from tkinter import messagebox

# Global variables for current webcam size and language
current_size = (320, 240)
current_lang = "de"


def set_current_lang(lang):
    """Set the current language globally."""
    global current_lang
    current_lang = lang


def toggle_size(scan_button, size_button):
    """
    Toggle the webcam resolution between two preset sizes.
    Updates the size button text accordingly.
    """
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
    """
    Show a confirmation dialog before exiting the program.
    """
    strings = LANGUAGES[current_lang]
    if messagebox.askyesno(strings["exit_dialog_title"], strings["exit_dialog_text"]):
        root.destroy()


def center_windowframe(root):
    """
    Center the main window on the screen.
    """
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """
    Main function to set up and run the CoinScan GUI application.
    """
    global current_lang, current_size

    # Create the main window
    root = tk.Tk()
    root.title("MünzScan")
    root.geometry("500x500")

    # Sidebar with icon buttons (Home, Settings, Down Arrow)
    sidebar = tk.Frame(root, bg="#2c3e50", width=60)
    sidebar.pack(side="left", fill="y")
    for icon in ["🏠", "⚙️", "⬇️"]:
        btn = tk.Button(
            sidebar, text=icon, bg="#2c3e50", fg="white", relief="flat", font=UI_FONT
        )
        btn.pack(pady=10)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Main content area
    content = tk.Frame(root, bg="white")
    content.pack(side="right", expand=True, fill="both")

    # Language selection frame with flag icons
    lang_frame = tk.Frame(content, bg="white")
    lang_frame.pack(pady=5)
    flag_images = {
        "de": ImageTk.PhotoImage(Image.open("flagicon/flag_DE.png").resize((24, 24))),
        "en": ImageTk.PhotoImage(Image.open("flagicon/flag_UK.png").resize((24, 24))),
    }

    widgets = {}

    # Menu bar with Exit option
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
    widgets["file_menu_cascade_index"] = 0

    # Language selection buttons
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
        lang_btn.image = flag_images[code]  # Prevent garbage collection
        lang_btn.pack(side="left", padx=5)
        lang_btn.bind("<Enter>", on_enter)
        lang_btn.bind("<Leave>", on_leave)

    # Title label
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

    # Recognition results listbox
    widgets["recognition"] = tk.Listbox(content, font=MONO_FONT, height=5)
    widgets["recognition"].pack(pady=5)

    # Total label (shows the sum of recognized coins)
    widgets["total_label"] = tk.Label(
        content, text=LANGUAGES[current_lang]["total"], font=UI_FONT, bg="white"
    )
    widgets["total_label"].pack(pady=10)

    # Scan button row
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


# Entry point: run the main function if this script is executed directly
if __name__ == "__main__":
    main()