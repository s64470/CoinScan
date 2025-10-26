# -*- coding: utf-8 -*-
import cv2
import threading
from PIL import Image, ImageTk


def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    # Disable the scan button to prevent multiple scans at once
    scan_button.config(state="disabled")

    def stream():
        # Open the default webcam (device 0)
        cap = cv2.VideoCapture(0)
        # Set the webcam resolution based on current_size
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        # If webcam is not available, show an error message in the recognition list
        if not cap.isOpened():
            msg = (
                "Webcam nicht verfügbar."
                if current_lang == "de"
                else "Webcam not available."
            )
            recognition.insert(0, msg)
            scan_button.config(state="normal")
            return

        # Main loop: read one frame from the webcam
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Simulate coin recognition (hardcoded coins for now)
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            # Clear previous recognition results
            recognition.delete(0, "end")
            # Insert recognized coins into the listbox
            for currency, value, symbol in coins:
                recognition.insert("end", f"{currency} {value} {symbol}")

            # Calculate and display the total value (hardcoded)
            total = 1.00 + 0.05
            total_text = (
                f"GESAMT: {total:.2f} €"
                if current_lang == "de"
                else f"TOTAL: €{total:.2f}"
            )
            total_label.config(text=total_text)

            # Convert the frame to RGB and resize for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb).resize(current_size)
            imgtk = ImageTk.PhotoImage(image=img)
            # Display the webcam image in the GUI
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)

            # Only process one frame per scan (remove 'break' for continuous streaming)
            break

        # Release the webcam and re-enable the scan button
        cap.release()
        scan_button.config(state="normal")

    # Run the stream function in a separate thread to avoid blocking the GUI
    threading.Thread(target=stream, daemon=True).start()