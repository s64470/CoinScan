# -*- coding: utf-8 -*-
import cv2
import threading
from PIL import Image, ImageTk
import numpy as np

def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    """Detect and display only the largest coin near the centre of the frame, with debug output for calibration."""
    scan_button.config(state="disabled")  # Disable scan button during scan

    def stream():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])
        if not cap.isOpened():
            scan_button.config(state="normal")
            return
        ret, frame = cap.read()
        if not ret:
            scan_button.config(state="normal")
            cap.release()
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 7)

        circles = cv2.HoughCircles(
            gray_blur,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=30,
            param1=50,
            param2=12,       # Lower for more sensitivity
            minRadius=10,    # Lower for smaller coins
            maxRadius=90,    # Higher for larger coins
        )

        recognition.delete(0, "end")
        found = False
        total = 0.0
        if circles is not None:
            circles = np.uint16(np.around(circles))
            frame_centre_x = frame.shape[1] // 2
            frame_centre_y = frame.shape[0] // 2
            tolerance_x = frame.shape[1] * 0.2  # 20% of width
            tolerance_y = frame.shape[0] * 0.2  # 20% of height

            # Find the largest coin near the centre
            centre_coins = [
                (x, y, r) for (x, y, r) in circles[0, :]
                if (abs(x - frame_centre_x) <= tolerance_x) and (abs(y - frame_centre_y) <= tolerance_y)
            ]
            if centre_coins:
                x, y, r = max(centre_coins, key=lambda c: c[2])
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)
                coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)
                coin_hue = coin_hsv[:, :, 0][mask == 255]
                mean_hue = np.mean(coin_hue)
                # --- Debug output for calibration ---
                print(f"Detected coin: radius={r}, mean_hue={mean_hue:.1f}")
                # --- Colour classification ---
                if mean_hue > 18 and mean_hue < 35:
                    colour_label = "Gold"
                elif mean_hue > 8 and mean_hue <= 18:
                    colour_label = "Copper"
                else:
                    colour_label = "Silver"
                # --- Size classification ---
                if colour_label == "Gold" and r > 52:
                    value = 2.00
                    label = "2€"
                elif colour_label == "Silver" and r > 42:
                    value = 1.00
                    label = "1€"
                elif colour_label == "Gold" and r > 32:
                    value = 0.50
                    label = "50ct"
                elif colour_label == "Gold" and r > 27:
                    value = 0.20
                    label = "20ct"
                elif colour_label == "Copper" and r > 22:
                    value = 0.10
                    label = "10ct"
                else:
                    value = 0.05
                    label = "Unknown"
                total += value
                recognition.insert(
                    "end",
                    f"Coin: {label} ({colour_label}, radius: {r}, hue: {mean_hue:.1f})"
                )
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                found = True

        if not found:
            msg = (
                "Keine Münze im Zentrum erkannt."
                if current_lang == "de"
                else "No coin detected in centre."
            )
            recognition.insert("end", msg)

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