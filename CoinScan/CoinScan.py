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
        "scan": "Münzen scannen",
        "exit": "Programm Beenden",
        "total": "GESAMT: 0,00 €",
        "size_plus": "+",
        "size_minus": "-",
    },
    "en": {
        "title": "LIVE SCAN",
        "scan": "Scan Coins",
        "exit": "Exit",
        "total": "TOTAL: €0.00",
        "size_plus": "+",
        "size_minus": "-",
    },
}


# Center the window
def center_windowframe():
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


# Exit Program
def exit_program():
    root.destroy()


# Toggle webcam preview size
def toggle_size():
    global current_size
    strings = LANGUAGES[current_lang]
    if current_size == (320, 240):
        current_size = (640, 480)
        size_button.config(text=strings["size_minus"])
    else:
        current_size = (320, 240)
        size_button.config(text=strings["size_plus"])


# Switch language
def switch_language(lang):
    global current_lang
    current_lang = lang
    strings = LANGUAGES[lang]

    title.config(text=strings["title"])
    scan_button.config(text=strings["scan"])
    exit_button.config(text=strings["exit"])
    total_label.config(text=strings["total"])
    size_button.config(
        text=(
            strings["size_plus"]
            if current_size == (320, 240)
            else strings["size_minus"]
        )
    )


# Webcam + recognition stream
def update_recognition():
    scan_button.config(state="disabled")

    def stream():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        if not cap.isOpened():
            recognition.insert(
                tk.END,
                (
                    "Webcam nicht verfügbar."
                    if current_lang == "de"
                    else "Webcam not available."
                ),
            )
            scan_button.config(state="normal")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Simulated recognition
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            recognition.delete(0, tk.END)
            for currency, value, symbol in coins:
                recognition.insert(tk.END, f"{currency} | {value} | {symbol}")

            total = 1.00 + 0.05
            total_text = (
                f"GESAMT: {total:.2f} €"
                if current_lang == "de"
                else f"TOTAL: €{total:.2f}"
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


# Main GUI
def main():
    global root, recognition, total_label, webcam_label, size_button, title, scan_button, exit_button

    root = tk.Tk()
    root.title("MünzScan")
    root.geometry("500x500")

    # Sidebar
    sidebar = tk.Frame(root, bg="#2c3e50", width=60)
    sidebar.pack(side="left", fill="y")

    for icon in ["🏠", "⚙️", "⬇️"]:
        btn = tk.Button(sidebar, text=icon, bg="#2c3e50", fg="white", relief="flat")
        btn.pack(pady=10)

    # Main content
    content = tk.Frame(root, bg="white")
    content.pack(side="right", expand=True, fill="both")

    # Language switch
    lang_frame = tk.Frame(content, bg="white")
    lang_frame.pack(pady=5)
    tk.Button(lang_frame, text="🇩🇪", command=lambda: switch_language("de")).pack(
        side="left", padx=5
    )
    tk.Button(lang_frame, text="🇬🇧", command=lambda: switch_language("en")).pack(
        side="left", padx=5
    )

    title = tk.Label(
        content, text=LANGUAGES[current_lang]["title"], font=("Arial", 14), bg="white"
    )
    title.pack(pady=10)

    webcam_row = tk.Frame(content, bg="white")
    webcam_row.pack(pady=5)

    webcam_label = tk.Label(webcam_row, bg="black")
    webcam_label.pack(side="left", padx=5)

    size_button = tk.Button(
        webcam_row, text=LANGUAGES[current_lang]["size_plus"], command=toggle_size
    )
    size_button.pack(side="left", padx=5)

    recognition = tk.Listbox(content, font=("Courier", 10), height=5)
    recognition.pack(pady=5)

    total_label = tk.Label(
        content, text=LANGUAGES[current_lang]["total"], font=("Arial", 12), bg="white"
    )
    total_label.pack(pady=10)

    scan_button = tk.Button(
        content, text=LANGUAGES[current_lang]["scan"], command=update_recognition
    )
    scan_button.pack(pady=5)

    exit_button = tk.Button(
        content, text=LANGUAGES[current_lang]["exit"], command=exit_program
    )
    exit_button.pack(pady=5)

    center_windowframe()
    root.mainloop()


# Run
if __name__ == "__main__":
    main()