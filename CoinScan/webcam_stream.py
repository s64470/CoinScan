# -*- coding: utf-8 -*-
# Webcam streaming and coin recognition simulation module.
# webcam_stream.py
import cv2
import threading
from PIL import Image, ImageTk


def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    """
    Handles webcam capture and (simulated) coin recognition.
    Updates the GUI with recognized coins and webcam image.

    Args:
        scan_button: The button widget used to start scanning (will be disabled during scan).
        recognition: The Listbox widget to display recognized coins.
        total_label: The Label widget to display the total value.
        webcam_label: The Label widget to display the webcam image.
        current_size: Tuple for webcam resolution (width, height).
        current_lang: Current language code ("de" or "en").
    """
    # Disable the scan button to prevent multiple scans at once
    scan_button.config(state="disabled")

    def stream():
        # Open the webcam (device 0)
        cap = cv2.VideoCapture(0)
        # Set webcam resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        # If webcam is not available, show an error message in the selected language
        if not cap.isOpened():
            msg = (
                "Webcam nicht verfügbar."
                if current_lang == "de"
                else "Webcam not available."
            )
            recognition.insert(0, msg)
            scan_button.config(state="normal")
            return

        # Main loop: read one frame and simulate coin recognition
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Simulate coin recognition (hardcoded coins)
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            recognition.delete(0, "end")  # Clear previous results
            for currency, value, symbol in coins:
                recognition.insert("end", f"{currency} {value} {symbol}")

            # Calculate total (hardcoded as 1.05)
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
            webcam_label.imgtk = imgtk  # Prevent garbage collection
            webcam_label.configure(image=imgtk)

            break  # Only process one frame for this simulation

        # Release the webcam
        cap.release()
        # Re-enable the scan button
        scan_button.config(state="normal")

    # Start the webcam stream in a separate thread to keep the UI responsive
    threading.Thread(target=stream, daemon=True).start()