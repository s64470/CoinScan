from __future__ import annotations
import threading
from typing import Tuple, Callable, Any, Dict, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter, ImageDraw

from language import LANGUAGES, format_total, get_text


Size = Tuple[int, int]


def classify_coin(mean_hue: float, radius: int) -> Tuple[float, str, str]:
    # Classify a coin by mean hue and radius.
    # Returns (value, label, colour_label).
    if 18 < mean_hue < 35:
        colour_label = "Gold"
    elif 8 < mean_hue <= 18:
        colour_label = "Copper"
    else:
        colour_label = "Silver"

    # Determine coin value based on colour and size thresholds.
    if colour_label == "Gold" and radius > 52:
        return 2.00, "2€", colour_label
    if colour_label == "Silver" and radius > 42:
        return 1.00, "1€", colour_label
    if colour_label == "Gold" and radius > 32:
        return 0.50, "50ct", colour_label
    if colour_label == "Gold" and radius > 27:
        return 0.20, "20ct", colour_label
    if colour_label == "Gold" and radius > 22:
        return 0.10, "10ct", colour_label
    if colour_label == "Copper" and radius > 21:
        return 0.05, "5ct", colour_label
    if colour_label == "Copper" and radius > 18:
        return 0.02, "2ct", colour_label
    if colour_label == "Copper" and radius > 15:
        return 0.01, "1ct", colour_label
    # Fallback for unrecognized coins
    return 0.00, "Unknown", colour_label


def centre_coins(
    circles: np.ndarray, frame_shape: Tuple[int, int, int]
) -> list[Tuple[int, int, int]]:
    # Filter detected circles to those near the frame centre.
    h, w = frame_shape[:2]
    fx, fy = w // 2, h // 2
    tolx, toly = w * 0.2, h * 0.2  # tolerance region (20% of width/height)
    return [
        (x, y, r)
        for (x, y, r) in circles
        if (abs(x - fx) <= tolx) and (abs(y - fy) <= toly)
    ]


def update_recognition(
    scan_button: Any,
    recognition: Any,
    total_label: Any,
    webcam_label: Any,
    current_size: Size,
    current_lang: str,
    on_results: Optional[Callable[[list[Tuple[float, str]]], None]] = None,
) -> None:
    """Run a single-frame capture and recognition.

    If `on_results` is provided it will be called on the Tk main thread with a
    list of tuples for each detected coin: (value, label).
    The function no longer inserts coin classification strings into the
    `recognition` listbox directly; the caller should insert display strings if
    desired. This allows the caller to maintain an editable model of detected
    coins for manual post-processing.
    """
    # Disable UI scan button and start a background stream thread
    scan_button.config(state="disabled")

    def stream() -> None:
        def ui(callable_obj: Callable, *args, **kwargs) -> None:
            # Schedule a callable on the Tkinter main thread if possible
            try:
                recognition.after(0, lambda: callable_obj(*args, **kwargs))
            except Exception:
                pass

        def set_webcam_image(pil_img: Image.Image) -> None:
            # Convert PIL image to a PhotoImage and set it on the label (prevent GC).
            try:
                imgtk = ImageTk.PhotoImage(image=pil_img)
                webcam_label.imgtk = imgtk  # prevent GC
                webcam_label.configure(image=imgtk)
                # If webcam preview is set, update the scan button to show "Rescan"
                try:
                    scan_button.config(text=get_text(current_lang, "rescan", "Rescan"))
                except Exception:
                    pass
            except Exception:
                pass

        cap: Optional[cv2.VideoCapture] = None
        try:
            # Open camera
            cap = cv2.VideoCapture(0)

            # Set requested capture size
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

            # Check camera opened successfully
            if not cap.isOpened():
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "camera_fail", "Camera open failed"),
                )
                return

            # Read one frame from camera
            ret, frame = cap.read()
            if not ret or frame is None:
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "frame_fail", "Frame read failed"),
                )
                return

            # Convert to grayscale for circle detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Reduce noise with median blur
            gray_blur = cv2.medianBlur(gray, 7)

            # Detect circles using Hough transform
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

            # Clear previous recognition messages
            ui(recognition.delete, 0, "end")
            found = False
            total = 0.0
            # Results now only include (value, label)
            results: list[Tuple[float, str]] = []

            # Variables to hold detected circle for display compositing
            detected_circle = None

            if circles is not None:
                # Round and convert circles to uint16 Nx3 array
                circles_uint = np.uint16(np.around(circles))[0, :]
                # Keep only circles near the centre
                ccoins = centre_coins(circles_uint, frame.shape)

                if ccoins:
                    # Choose the largest centred coin
                    x, y, r = max(ccoins, key=lambda c: c[2])

                    # Create mask for coin region and extract pixels
                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r, 255, -1)
                    coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)

                    # Convert masked coin region to HSV for hue analysis
                    coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)

                    # Compute mean hue inside the mask
                    coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                    mean_hue = float(np.mean(coin_hue)) if coin_hue.size > 0 else 0.0

                    # Classify coin by hue and radius
                    value, label, colour_label = classify_coin(mean_hue, r)

                    total += value
                    # Collect only the minimal structured result (value, label).
                    results.append((value, label))

                    # Insert a simple coin entry into the recognition listbox (no colour, radius or hue)
                    if on_results is None:
                        ui(recognition.insert, "end", label)

                    # Save detected circle for later compositing on the display image.
                    detected_circle = (int(x), int(y), int(r))
                    found = True

            if not found:
                # Inform user no coin was detected in centre area
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "no_coin", "No coin detected in centre."),
                )

            # Notify caller with structured results (may be empty)
            if on_results is not None:
                try:
                    ui(on_results, results)
                except Exception:
                    pass
            else:
                # Only update total_label here when no on_results handler is provided.
                ui(total_label.config, text=format_total(current_lang, total))

            # Convert BGR to RGB for PIL and resize for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            resized = cv2.resize(
                frame_rgb, current_size, interpolation=cv2.INTER_LINEAR
            )

            # Convert NumPy array to PIL Image
            img = Image.fromarray(resized)

            # If a coin was detected, blur everything outside the detected circle.
            try:
                if detected_circle is not None:
                    # Scale circle coordinates from capture frame to resized image
                    orig_h, orig_w = frame_rgb.shape[:2]
                    dst_w, dst_h = current_size
                    sx = dst_w / orig_w
                    sy = dst_h / orig_h
                    # Use uniform scale (frame aspect preserved) for radius
                    scale = (sx + sy) / 2.0
                    x_s = int(detected_circle[0] * sx)
                    y_s = int(detected_circle[1] * sy)
                    r_s = max(1, int(detected_circle[2] * scale))

                    # Create a blurred version of the whole image
                    blur_radius = max(15, r_s // 2)

                    # Use a median filter (PIL's MedianFilter) instead of Gaussian blur.
                    # MedianFilter requires an odd-sized kernel; map blur_radius to an odd size.
                    kernel = max(3, (int(blur_radius) // 2) * 2 + 1)
                    blurred = img.filter(ImageFilter.MedianFilter(size=kernel))

                    # Create mask with white circle where the coin is (keep sharp)
                    mask = Image.new("L", img.size, 0)
                    draw_mask = ImageDraw.Draw(mask)
                    bbox = (x_s - r_s, y_s - r_s, x_s + r_s, y_s + r_s)
                    draw_mask.ellipse(bbox, fill=255)

                    # Composite: keep original (sharp) inside circle, blurred outside
                    img = Image.composite(img, blurred, mask)

                    # Draw annotation circle and center dot on the composited image
                    draw = ImageDraw.Draw(img)
                    # green ring
                    ring_width = max(2, int(max(1, r_s * 0.06)))
                    outline_bbox = (bbox[0], bbox[1], bbox[2], bbox[3])
                    draw.ellipse(outline_bbox, outline="rgb(0,255,0)", width=ring_width)
                    # small red center
                    center_r = max(2, r_s // 15)
                    draw.ellipse(
                        (
                            x_s - center_r,
                            y_s - center_r,
                            x_s + center_r,
                            y_s + center_r,
                        ),
                        fill="rgb(255,0,0)",
                    )
            except Exception:
                # If anything goes wrong, fall back to the unmodified image
                pass

            # Set image on the webcam label (UI)
            ui(set_webcam_image, img)
        finally:
            # Ensure camera is released and UI button re-enabled
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass
            ui(scan_button.config, state="normal")

    threading.Thread(target=stream, daemon=True).start()