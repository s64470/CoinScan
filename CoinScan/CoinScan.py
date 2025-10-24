from PIL import Image, ImageTk
import tkinter as tk
import cv2
import threading

# Global preview size and language
current_size = (320, 240)
current_lang = "de"

# Language dictionary
LANGUAGES = {
    "de": {
        "title": "LIVE SCAN",
        "scan": "🔍 Münzen scannen",
        "exit": "❌ Programm Beenden",
        "total": "GESAMT: 0,00 €",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
    },
    "en": {
        "title": "LIVE SCAN",
        "scan": "🔍 Scan Coins",
        "exit": "❌ Exit",
        "total": "TOTAL: €0.00",
        "size_plus": "🔎 +",
        "size_minus": "🔎 -",
    },
}

# Font styles
UI_FONT = ("Verdana", 11)
TITLE_FONT = ("Verdana", 14, "bold")
MONO_FONT = ("Consolas", 10)

# Button style
BUTTON_STYLE = {
    "font": UI_FONT,
    "bg": "#3498db",
    "fg": "white",
    "activebackground": "#2980b9",
    "activeforeground": "white",
    "relief": "raised",
    "bd": 2,
    "padx": 10,
    "pady": 5,
}

def on_enter(e):
    e.widget["background"] = "#2980b9"

def on_leave(e):
    e.widget["background"] = "#3498db"

def center_windowframe():
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

def exit_program():
    root.destroy()

def toggle_size():
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

def switch_language(lang):
    global current_lang
    current_lang = lang
    strings = LANGUAGES[lang]

    title.config(text=strings["title"])
    scan_button.config(text=strings["scan"])
    exit_button.config(text=strings["exit"])
    total_label.config(text=strings["total"])
    size_button.config(
        text=(strings["size_plus"] if current_size == (320, 240) else strings["size_minus"])
    )

def update_recognition():
    scan_button.config(state="disabled")

    def stream():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        if not cap.isOpened():
            recognition.insert(
                tk.END,
                ("Webcam nicht verfügbar." if current_lang == "de" else "Webcam not available."),
            )
            scan_button.config(state="normal")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            recognition.delete(0, tk.END)
            for currency, value, symbol in coins:
                recognition.insert(tk.END, f"{currency} | {value} | {symbol}")

            total = 1.00 + 0.05
            total_text = (
                f"GESAMT: {total:.2f} €" if current_lang == "de" else f"TOTAL: €{total:.2f}"
            )
            total_label.config(text=total_text)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb).resize(current_size)
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)

        cap.release()
        scan_button.config(state="normal")

    threading.Thread(target=stream, daemon=True).start()

def main():
    global root, recognition, total_label, webcam_label, size_button, title, scan_button, exit_button

    root = tk.Tk()
    root.title("MünzScan")
    root.geometry("500x500")

    sidebar = tk.Frame(root, bg="#2c3e50", width=60)
    sidebar.pack(side="left", fill="y")

    for icon in ["🏠", "⚙️", "⬇️"]:
        btn = tk.Button(sidebar, text=icon, bg="#2c3e50", fg="white", relief="flat", font=UI_FONT)
        btn.pack(pady=10)

    content = tk.Frame(root, bg="white")
    content.pack(side="right", expand=True, fill="both")

    lang_frame = tk.Frame(content, bg="white")
    lang_frame.pack(pady=5)
    for code, flag in [("de", "🇩🇪"), ("en", "🇬🇧")]:
        lang_btn = tk.Button(lang_frame, text=flag, command=lambda c=code: switch_language(c), **BUTTON_STYLE)
        lang_btn.pack(side="left", padx=5)
        lang_btn.bind("<Enter>", on_enter)
        lang_btn.bind("<Leave>", on_leave)

    title = tk.Label(content, text=LANGUAGES[current_lang]["title"], font=TITLE_FONT, bg="white")
    title.pack(pady=10)

    webcam_row = tk.Frame(content, bg="white")
    webcam_row.pack(pady=5)

    webcam_label = tk.Label(webcam_row, bg="black")
    webcam_label.pack(side="left", padx=5)

    size_button = tk.Button(webcam_row, text=LANGUAGES[current_lang]["size_plus"], command=toggle_size, **BUTTON_STYLE)
    size_button.pack(side="left", padx=5)
    size_button.bind("<Enter>", on_enter)
    size_button.bind("<Leave>", on_leave)

    recognition = tk.Listbox(content, font=MONO_FONT, height=5)
    recognition.pack(pady=5)

    total_label = tk.Label(content, text=LANGUAGES[current_lang]["total"], font=UI_FONT, bg="white")
    total_label.pack(pady=10)

    button_frame = tk.Frame(content, bg="white")
    button_frame.pack(pady=10)

    scan_button = tk.Button(button_frame, text=LANGUAGES[current_lang]["scan"], command=update_recognition, **BUTTON_STYLE)
    scan_button.pack(side="left", padx=5)
    scan_button.bind("<Enter>", on_enter)
    scan_button.bind("<Leave>", on_leave)

    exit_button = tk.Button(button_frame, text=LANGUAGES[current_lang]["exit"], command=exit_program, **BUTTON_STYLE)
    exit_button.pack(side="left", padx=5)
    exit_button.bind("<Enter>", on_enter)
    exit_button.bind("<Leave>", on_leave)

    center_windowframe()
    root.mainloop()

if __name__ == "__main__":
    main()