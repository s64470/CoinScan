# -*- coding: utf-8 -*-
# main.py

import tkinter as tk
from ui_config import UI_FONT, TITLE_FONT, MONO_FONT, BUTTON_STYLE, on_enter, on_leave
from language import LANGUAGES, switch_language
from webcam_stream import update_recognition

current_size = (320, 240)
current_lang = "de"


def toggle_size(scan_button, size_button):
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
    root.destroy()


def center_windowframe(root):
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    global current_lang, current_size

    root = tk.Tk()
    root.title("MünzScan")
    root.geometry("500x500")

    sidebar = tk.Frame(root, bg="#2c3e50", width=60)
    sidebar.pack(side="left", fill="y")
    for icon in ["🏠", "⚙️", "⬇️"]:
        btn = tk.Button(
            sidebar, text=icon, bg="#2c3e50", fg="white", relief="flat", font=UI_FONT
        )
        btn.pack(pady=10)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    content = tk.Frame(root, bg="white")
    content.pack(side="right", expand=True, fill="both")

    lang_frame = tk.Frame(content, bg="white")
    lang_frame.pack(pady=5)

    widgets = {}

    for code, flag in [("de", "🇩🇪"), ("en", "🇬🇧")]:
        lang_btn = tk.Button(
            lang_frame,
            text=flag,
            command=lambda c=code: switch_language(c, widgets, current_size),
            **BUTTON_STYLE,
        )
        lang_btn.pack(side="left", padx=5)
        lang_btn.bind("<Enter>", on_enter)
        lang_btn.bind("<Leave>", on_leave)

    widgets["title"] = tk.Label(
        content, text=LANGUAGES[current_lang]["title"], font=TITLE_FONT, bg="white"
    )
    widgets["title"].pack(pady=10)

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

    widgets["recognition"] = tk.Listbox(content, font=MONO_FONT, height=5)
    widgets["recognition"].pack(pady=5)

    widgets["total_label"] = tk.Label(
        content, text=LANGUAGES[current_lang]["total"], font=UI_FONT, bg="white"
    )
    widgets["total_label"].pack(pady=10)

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

    widgets["exit_button"] = tk.Button(
        button_frame,
        text=LANGUAGES[current_lang]["exit"],
        command=lambda: exit_program(root),
        **BUTTON_STYLE,
    )
    widgets["exit_button"].pack(side="left", padx=5)
    widgets["exit_button"].bind("<Enter>", on_enter)
    widgets["exit_button"].bind("<Leave>", on_leave)

    center_windowframe(root)
    root.mainloop()


if __name__ == "__main__":
    main()