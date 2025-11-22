from __future__ import annotations
import threading
from typing import Tuple, Callable, Any, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter, ImageDraw

from language import format_total, get_text


Size = Tuple[int, int]


def classify_coin(mean_hue: float, radius: int) -> Tuple[float, str, str]:
    """Classify a coin by mean hue and radius.

    Returns a tuple: (value, label, colour_label).
    """
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
    """Filter detected circles to those near the frame centre.

    `frame_shape` is expected to be the NumPy shape (height, width, channels).
    """
    height, width = frame_shape[:2]
    cx, cy = width // 2, height // 2
    tolx, toly = width * 0.2, height * 0.2  # 20% tolerance of width/height
    return [
        (x, y, r)
        for (x, y, r) in circles
        if (abs(x - cx) <= tolx) and (abs(y - cy) <= toly)
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

    If `on_results` is provided it will be called (on the Tk thread) with a
    list of tuples: (value, label) for each detected coin.

    The function avoids inserting complex strings into the `recognition`
    widget when `on_results` is supplied so the caller can manage the
    display/model.
    """
    scan_button.config(state="disabled")

    def stream() -> None:
        def ui(callable_obj: Callable, *args, **kwargs) -> None:
            # Schedule a callable on the Tk main thread if possible.
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
                try:
                    scan_button.config(text=get_text(current_lang, "rescan", "Rescan"))
                except Exception:
                    pass
            except Exception:
                pass

        cap: Optional[cv2.VideoCapture] = None
        try:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])

            if not cap.isOpened():
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "camera_fail", "Camera open failed"),
                )
                return

            ret, frame = cap.read()
            if not ret or frame is None:
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "frame_fail", "Frame read failed"),
                )
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_blur = cv2.medianBlur(gray, 7)

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

            ui(recognition.delete, 0, "end")
            total = 0.0
            results: list[Tuple[float, str]] = []
            detected_circle: Optional[tuple[int, int, int]] = None

            if circles is not None:
                circles_uint = np.uint16(np.around(circles))[0, :]
                ccoins = centre_coins(circles_uint, frame.shape)

                if ccoins:
                    x, y, r = max(ccoins, key=lambda c: c[2])

                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r, 255, -1)
                    coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)

                    coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)
                    coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                    mean_hue = float(np.mean(coin_hue)) if coin_hue.size > 0 else 0.0

                    value, label, _ = classify_coin(mean_hue, r)
                    total += value
                    results.append((value, label))

                    if on_results is None:
                        ui(recognition.insert, "end", label)

                    detected_circle = (int(x), int(y), int(r))

            if detected_circle is None:
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "no_coin", "No coin detected in centre."),
                )

            # Notify caller with structured results (on UI thread)
            if on_results is not None:
                try:
                    ui(on_results, results)
                except Exception:
                    pass
            else:
                ui(total_label.config, text=format_total(current_lang, total))

            # Prepare display image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(frame_rgb, current_size, interpolation=cv2.INTER_LINEAR)
            img = Image.fromarray(resized)

            # If detected, blur outside coin and draw annotations
            try:
                if detected_circle is not None:
                    orig_h, orig_w = frame_rgb.shape[:2]
                    dst_w, dst_h = current_size
                    sx = dst_w / orig_w
                    sy = dst_h / orig_h
                    scale = (sx + sy) / 2.0
                    x_s = int(detected_circle[0] * sx)
                    y_s = int(detected_circle[1] * sy)
                    r_s = max(1, int(detected_circle[2] * scale))

                    blur_radius = max(15, r_s // 2)
                    kernel = max(3, (int(blur_radius) // 2) * 2 + 1)
                    blurred = img.filter(ImageFilter.MedianFilter(size=kernel))

                    mask = Image.new("L", img.size, 0)
                    draw_mask = ImageDraw.Draw(mask)
                    bbox = (x_s - r_s, y_s - r_s, x_s + r_s, y_s + r_s)
                    draw_mask.ellipse(bbox, fill=255)

                    img = Image.composite(img, blurred, mask)

                    draw = ImageDraw.Draw(img)
                    ring_width = max(2, int(max(1, r_s * 0.06)))
                    draw.ellipse(bbox, outline="rgb(0,255,0)", width=ring_width)
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
                pass

            ui(set_webcam_image, img)
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass
            ui(scan_button.config, state="normal")

    threading.Thread(target=stream, daemon=True).start()