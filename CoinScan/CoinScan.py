from PIL import Image, ImageTk
import tkinter as tk
import cv2
import threading

# Global preview size
current_size = (320, 240)


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
    if current_size == (320, 240):
        current_size = (640, 480)
        size_button.config(text="-")
    else:
        current_size = (320, 240)
        size_button.config(text="+")


# Webcam + recognition stream
def update_recognition():
    def stream():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Simulate recognition logic
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            recognition.delete(0, tk.END)
            for currency, value, symbol in coins:
                recognition.insert(tk.END, f"{currency} | {value} | {symbol}")
            total_label.config(text="GESAMT: 1,05 €")

            # Convert frame to RGB and resize
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb).resize(current_size)
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)

        cap.release()

    threading.Thread(target=stream, daemon=True).start()


# Main GUI
def main():
    global root, recognition, total_label, webcam_label, size_button

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

    title = tk.Label(content, text="LIVE SCAN", font=("Arial", 14), bg="white")
    title.pack(pady=10)

    # Webcam + size button in one row
    webcam_row = tk.Frame(content, bg="white")
    webcam_row.pack(pady=5)

    webcam_label = tk.Label(webcam_row, bg="black")
    webcam_label.pack(side="left", padx=5)

    size_button = tk.Button(webcam_row, text="+", command=toggle_size)
    size_button.pack(side="left", padx=5)

    recognition = tk.Listbox(content, font=("Courier", 10), height=5)
    recognition.pack(pady=5)

    total_label = tk.Label(
        content, text="GESAMT: 0,00 €", font=("Arial", 12), bg="white"
    )
    total_label.pack(pady=10)

    scan_button = tk.Button(content, text="Scan Coins", command=update_recognition)
    scan_button.pack(pady=5)

    exit_button = tk.Button(content, text="Exit", command=exit_program)
    exit_button.pack(pady=5)

    center_windowframe()
    root.mainloop()


# Run
if __name__ == "__main__":
    main()