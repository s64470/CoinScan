# -*- coding: utf-8 -*-
# webcam_stream.py

import cv2
import threading

from PIL import Image, ImageTk


def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    scan_button.config(state="disabled")

    def stream():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

        if not cap.isOpened():
            msg = (
                "Webcam nicht verfügbar."
                if current_lang == "de"
                else "Webcam not available."
            )

            recognition.insert(0, msg)
            scan_button.config(state="normal")
            return

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Dummy coin data
            coins = [("EURO", "1€", "€"), ("EURO", "5 ct", "5")]
            recognition.delete(0, "end")

            for currency, value, symbol in coins:
                recognition.insert("end", f"{currency} | {value} | {symbol}")

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