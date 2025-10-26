# -*- coding: utf-8 -*-
# webcam_stream.py

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

        # Main loop: read frames from the webcam
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Dummy coin data for demonstration purposes
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            # Clear previous recognition results
            recognition.delete(0, "end")
            # Insert dummy coin data into the recognition listbox
            for currency, value, symbol in coins:
                recognition.insert("end", f"{currency} {value} {symbol}")

            # Calculate total value (hardcoded for demo)
            total = 1.00 + 0.05
            total_text = (
                f"GESAMT: {total:.2f} €"
                if current_lang == "de"
                else f"TOTAL: €{total:.2f}"
            )
            # Update the total label with the calculated value
            total_label.config(text=total_text)

            # Convert the frame from BGR (OpenCV) to RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the frame to a PIL image and resize it
            img = Image.fromarray(frame_rgb).resize(current_size)
            # Convert the PIL image to a Tkinter-compatible image
            imgtk = ImageTk.PhotoImage(image=img)
            # Display the image in the webcam_label widget
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)

        # Release the webcam when done
        cap.release()
        # Re-enable the scan button
        scan_button.config(state="normal")

    # Start the stream function in a separate thread to avoid blocking the GUI
    threading.Thread(target=stream, daemon=True).start()