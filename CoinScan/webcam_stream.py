# webcam_stream.py
# Handles webcam capture and coin recognition logic for CoinScan
"""
Module for capturing a single frame from the webcam, detecting a coin near the
centre of the frame, estimating its colour and size, mapping that to a euro
denomination and updating the UI widgets.
"""

import cv2
import threading
from PIL import Image, ImageTk
import numpy as np
import time


def update_recognition(
    scan_button, recognition, total_label, webcam_label, current_size, current_lang
):
    """
    Start a background thread to:
    - Grab a single frame from the default webcam.
    - Detect circular shapes (coins) using Hough Circle Transform.
    - Filter coins near the frame centre and choose the largest central coin.
    - Estimate coin colour by mean HSV hue within the coin mask.
    - Map colour+radius to a value/label (calibration thresholds are used).
    - Update UI widgets: a listbox-like `recognition`, a `total_label` and the
      `webcam_label` image. The `scan_button` is disabled while scanning.
    Parameters:
      scan_button: UI button widget that triggers the scan (will be disabled).
      recognition: UI list widget to display recognition results (cleared then updated).
      total_label: UI label to show total amount detected.
      webcam_label: UI label/widget where the frame image is shown.
      current_size: tuple(width, height) used to set webcam resolution and resize image.
      current_lang: "de" for German messages, any other value for English.
    """
    # Disable scan button to prevent concurrent scans (main thread)
    scan_button.config(state="disabled")

    def stream():
        times = {}

        def tic(name: str):
            times[name] = -time.perf_counter()

        def toc(name: str):
            times[name] += time.perf_counter()

        # Helper to marshal UI updates back to the Tk main thread
        def ui(callable_obj, *args, **kwargs):
            try:
                recognition.after(0, lambda: callable_obj(*args, **kwargs))
            except Exception:
                # If widget is destroyed, ignore UI updates
                pass

        # Special helper to set the webcam image on the main thread
        def set_webcam_image(pil_img: Image.Image):
            try:
                imgtk = ImageTk.PhotoImage(image=pil_img)
                webcam_label.imgtk = imgtk  # keep reference
                webcam_label.configure(image=imgtk)
            except Exception:
                pass

        cap = None
        try:
            # Open default camera (index 0) and try to set requested resolution.
            tic("camera_open")
            cap = cv2.VideoCapture(0)
            toc("camera_open")

            tic("set_props")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])
            toc("set_props")

            if not cap.isOpened():
                # If webcam couldn't be opened, re-enable button and exit.
                ui(recognition.insert, "end", "Perf: camera_open_failed")
                return

            # Grab a single frame from the camera
            tic("read")
            ret, frame = cap.read()
            toc("read")
            if not ret:
                # If frame capture failed, release camera, re-enable button and exit.
                ui(recognition.insert, "end", "Perf: frame_read_failed")
                return

            # Convert to grayscale and apply median blur to reduce noise prior to circle detection.
            tic("cvt_gray")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            toc("cvt_gray")

            tic("median_blur")
            gray_blur = cv2.medianBlur(gray, 7)
            toc("median_blur")

            # HoughCircles circle detection
            tic("hough")
            circles = cv2.HoughCircles(
                gray_blur,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=30,
                param1=50,
                param2=16,
                minRadius=15,
                maxRadius=90,
            )
            toc("hough")

            # Prepare UI output variables
            ui(recognition.delete, 0, "end")  # Clear previous recognition results
            found = False
            total = 0.0

            if circles is not None:
                # Round circle parameters to unsigned 16-bit ints (x, y, radius)
                tic("postprocess_circles")
                circles = np.uint16(np.around(circles))

                # Compute centre of the frame and tolerances (20% of frame size)
                frame_centre_x = frame.shape[1] // 2
                frame_centre_y = frame.shape[0] // 2
                tolerance_x = frame.shape[1] * 0.2
                tolerance_y = frame.shape[0] * 0.2

                # Filter detected circles to those whose centres lie within the central tolerance box.
                centre_coins = [
                    (x, y, r)
                    for (x, y, r) in circles[0, :]
                    if (abs(x - frame_centre_x) <= tolerance_x)
                    and (abs(y - frame_centre_y) <= tolerance_y)
                ]
                toc("postprocess_circles")

                if centre_coins:
                    # If multiple central coins, pick the largest (assumes closest coin is relevant)
                    x, y, r = max(centre_coins, key=lambda c: c[2])

                    # Create a mask for the detected coin region and extract coin pixels.
                    tic("mask")
                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r, 255, -1)
                    coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)
                    toc("mask")

                    # Convert masked coin region to HSV and compute mean hue for colour estimation.
                    tic("cvt_hsv")
                    coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)
                    toc("cvt_hsv")

                    tic("mean_hue")
                    coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                    mean_hue = np.mean(coin_hue) if coin_hue.size > 0 else 0.0
                    toc("mean_hue")

                    # Log detection details to console (useful for calibration/debugging)
                    print(f"Detected coin: radius={r}, mean_hue={mean_hue:.1f}")

                    # --- Calibration Section ---
                    # Determine a simple colour label based on mean hue thresholds.
                    # These thresholds depend heavily on lighting, camera and coin surface.
                    tic("classify")
                    if 18 < mean_hue < 35:
                        colour_label = "Gold"
                    elif 8 < mean_hue <= 18:
                        colour_label = "Copper"
                    else:
                        colour_label = "Silver"

                    # Map colour and radius to a euro coin value and label.
                    # These radius thresholds are heuristics and should be calibrated for your camera.
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
                    toc("classify")

                    # Accumulate total and update recognition list widget with details.
                    total += value
                    ui(
                        recognition.insert,
                        "end",
                        f"Coin: {label} ({colour_label}, radius: {r}, hue: {mean_hue:.1f})",
                    )

                    # Draw annotation circles on the frame for visual feedback (green circle + red centre dot).
                    tic("annotate")
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                    toc("annotate")
                    found = True

            # If no coin was detected, show a localized message in the recognition widget.
            if not found:
                msg = (
                    "Keine Münze im Zentrum erkannt."
                    if current_lang == "de"
                    else "No coin detected in centre."
                )
                ui(recognition.insert, "end", msg)

            # Update the total label using the selected language formatting.
            tic("update_total")
            total_text = (
                f"GESAMT: {total:.2f} €"
                if current_lang == "de"
                else f"TOTAL: €{total:.2f}"
            )
            ui(total_label.config, text=total_text)
            toc("update_total")

            # Convert frame to RGB, resize for the UI with OpenCV, then show via PIL/Tk.
            tic("cvt_rgb")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            toc("cvt_rgb")

            tic("cv_resize")
            resized = cv2.resize(
                frame_rgb,
                (current_size[0], current_size[1]),
                interpolation=cv2.INTER_LINEAR,
            )
            toc("cv_resize")

            tic("to_pil")
            img = Image.fromarray(resized)
            toc("to_pil")

            # Create PhotoImage and update label on main thread
            tic("photoimage")
            ui(set_webcam_image, img)
            toc("photoimage")

        finally:
            # Release the camera and re-enable the scan button.
            if cap is not None:
                tic("release")
                try:
                    cap.release()
                except Exception:
                    pass
                toc("release")
            ui(scan_button.config, state="normal")

            # Summarize perf metrics in ms
            if times:
                times_ms = {k: int(v * 1000) for k, v in times.items()}
                ordered_keys = [
                    "camera_open",
                    "set_props",
                    "read",
                    "cvt_gray",
                    "median_blur",
                    "hough",
                    "postprocess_circles",
                    "mask",
                    "cvt_hsv",
                    "mean_hue",
                    "classify",
                    "annotate",
                    "update_total",
                    "cvt_rgb",
                    "cv_resize",
                    "to_pil",
                    "photoimage",
                    "label_configure",
                    "release",
                ]
                summary = "Perf:" + ", ".join(
                    f"{k}={times_ms[k]}ms" for k in ordered_keys if k in times_ms
                )
                try:
                    ui(recognition.insert, "end", summary)
                except Exception:
                    pass
                print("Perf details (ms):", times_ms)

    # Launch the capture & recognition in a daemon thread to keep the main UI responsive.
    threading.Thread(target=stream, daemon=True).start()