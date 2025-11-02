# webcam_stream.py
# Handles webcam capture and coin recognition logic for CoinScan

import cv2
import threading
from PIL import Image, ImageTk
import numpy as np


def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    """
    Starts a thread to capture a frame from the webcam, detect coins,
    classify them by colour and size, and update the UI accordingly.
    """
    scan_button.config(state="disabled")  # Disable scan button during scan

    def stream():
        # Open webcam and set resolution
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

        # Preprocess frame for circle (coin) detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 7)
        circles = cv2.HoughCircles(
            gray_blur,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=30,
            param1=50,
            param2=12,
            minRadius=10,
            maxRadius=90,
        )

        recognition.delete(0, "end")  # Clear previous recognition results
        found = False
        total = 0.0

        if circles is not None:
            circles = np.uint16(np.around(circles))
            frame_centre_x = frame.shape[1] // 2
            frame_centre_y = frame.shape[0] // 2
            tolerance_x = frame.shape[1] * 0.2
            tolerance_y = frame.shape[0] * 0.2
            # Filter coins near the centre of the frame
            centre_coins = [
                (x, y, r)
                for (x, y, r) in circles[0, :]
                if (abs(x - frame_centre_x) <= tolerance_x)
                and (abs(y - frame_centre_y) <= tolerance_y)
            ]
            if centre_coins:
                # Use the largest coin in the centre
                x, y, r = max(centre_coins, key=lambda c: c[2])
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)
                coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)
                # Use float64 to avoid overflow in mean calculation
                coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                mean_hue = np.mean(coin_hue) if coin_hue.size > 0 else 0.0
                print(f"Detected coin: radius={r}, mean_hue={mean_hue:.1f}")

                # Classify coin by hue and radius
                if 18 < mean_hue < 35:
                    colour_label = "Gold"
                elif 8 < mean_hue <= 18:
                    colour_label = "Copper"
                else:
                    colour_label = "Silver"

                # Assign value and label based on colour and size
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
                    f"Coin: {label} ({colour_label}, radius: {r}, hue: {mean_hue:.1f})",
                )
                # Draw detected coin on frame
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                found = True

        # If no coin found, show message in selected language
        if not found:
            msg = (
                "Keine Münze im Zentrum erkannt."
                if current_lang == "de"
                else "No coin detected in centre."
            )
            recognition.insert("end", msg)

        # Update total label in selected language
        total_text = (
            f"GESAMT: {total:.2f} €" if current_lang == "de" else f"TOTAL: €{total:.2f}"
        )
        total_label.config(text=total_text)

        # Update webcam image in UI
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb).resize(current_size)
        imgtk = ImageTk.PhotoImage(image=img)
        webcam_label.imgtk = imgtk
        webcam_label.configure(image=imgtk)
        cap.release()
        scan_button.config(state="normal")

    # Start recognition in a separate thread to keep UI responsive
    threading.Thread(target=stream, daemon=True).start()