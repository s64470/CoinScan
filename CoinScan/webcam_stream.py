# webcam_stream.py
"""Webcam capture and coin recognition logic.

Provides a single entry point `update_recognition` that performs a
single capture + recognition pass, updates the UI asynchronously and
reports timing information for profiling.
"""

from __future__ import annotations
import threading
import time
from typing import Tuple, Callable, Any, Dict, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk

from language import LANGUAGES, format_total, get_text

# Type aliases for readability
Size = Tuple[int, int]

# ---------------------------------------------------------------------------
# Helper functions (pure logic, easier to test)
# ---------------------------------------------------------------------------


def classify_coin(mean_hue: float, radius: int) -> Tuple[float, str, str]:
    """Return (value, label, colour_label) based on hue + radius heuristics."""
    if 18 < mean_hue < 35:
        colour_label = "Gold"
    elif 8 < mean_hue <= 18:
        colour_label = "Copper"
    else:
        colour_label = "Silver"

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
    return 0.00, "Unknown", colour_label


def centre_coins(
    circles: np.ndarray, frame_shape: Tuple[int, int, int]
) -> list[Tuple[int, int, int]]:
    """Filter circles to those near the frame centre within tolerance."""
    h, w = frame_shape[:2]
    fx, fy = w // 2, h // 2
    tolx, toly = w * 0.2, h * 0.2
    return [
        (x, y, r)
        for (x, y, r) in circles
        if (abs(x - fx) <= tolx) and (abs(y - fy) <= toly)
    ]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def update_recognition(
    scan_button: Any,
    recognition: Any,
    total_label: Any,
    webcam_label: Any,
    current_size: Size,
    current_lang: str,
) -> None:
    """Capture one frame from the default webcam and attempt coin recognition.

    Updates UI elements via thread-safe Tk callbacks. Keeps behaviour the same
    but centralises localisation and formatting.
    """
    scan_button.config(state="disabled")

    def stream() -> None:
        times: Dict[str, float] = {}

        def tic(name: str) -> None:
            times[name] = -time.perf_counter()

        def toc(name: str) -> None:
            times[name] += time.perf_counter()

        def ui(callable_obj: Callable, *args, **kwargs) -> None:
            """Thread-safe UI dispatcher (ignores exceptions)."""
            try:
                recognition.after(0, lambda: callable_obj(*args, **kwargs))
            except Exception:
                pass

        def set_webcam_image(pil_img: Image.Image) -> None:
            try:
                imgtk = ImageTk.PhotoImage(image=pil_img)
                webcam_label.imgtk = imgtk  # prevent GC
                webcam_label.configure(image=imgtk)
            except Exception:
                pass

        cap: Optional[cv2.VideoCapture] = None
        try:
            tic("camera_open")
            cap = cv2.VideoCapture(0)
            toc("camera_open")

            tic("set_props")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, current_size[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, current_size[1])
            toc("set_props")

            if not cap.isOpened():
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "camera_fail", "Camera open failed"),
                )
                return

            tic("read")
            ret, frame = cap.read()
            toc("read")
            if not ret or frame is None:
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "frame_fail", "Frame read failed"),
                )
                return

            tic("cvt_gray")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            toc("cvt_gray")

            tic("median_blur")
            gray_blur = cv2.medianBlur(gray, 7)
            toc("median_blur")

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

            ui(recognition.delete, 0, "end")
            found = False
            total = 0.0

            if circles is not None:
                tic("postprocess_circles")
                circles_uint = np.uint16(np.around(circles))[0, :]
                ccoins = centre_coins(circles_uint, frame.shape)
                toc("postprocess_circles")

                if ccoins:
                    x, y, r = max(ccoins, key=lambda c: c[2])

                    tic("mask")
                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r, 255, -1)
                    coin_pixels = cv2.bitwise_and(frame, frame, mask=mask)
                    toc("mask")

                    tic("cvt_hsv")
                    coin_hsv = cv2.cvtColor(coin_pixels, cv2.COLOR_BGR2HSV)
                    toc("cvt_hsv")

                    tic("mean_hue")
                    coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                    mean_hue = float(np.mean(coin_hue)) if coin_hue.size > 0 else 0.0
                    toc("mean_hue")

                    tic("classify")
                    value, label, colour_label = classify_coin(mean_hue, r)
                    toc("classify")

                    total += value
                    ui(
                        recognition.insert,
                        "end",
                        f"Coin: {label} ({colour_label}, r={r}, hue={mean_hue:.1f})",
                    )

                    tic("annotate")
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                    toc("annotate")
                    found = True

            if not found:
                ui(
                    recognition.insert,
                    "end",
                    get_text(current_lang, "no_coin", "No coin detected in centre."),
                )

            tic("update_total")
            ui(total_label.config, text=format_total(current_lang, total))
            toc("update_total")

            tic("cvt_rgb")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            toc("cvt_rgb")

            tic("cv_resize")
            resized = cv2.resize(
                frame_rgb, current_size, interpolation=cv2.INTER_LINEAR
            )
            toc("cv_resize")

            tic("to_pil")
            img = Image.fromarray(resized)
            toc("to_pil")

            tic("photoimage")
            ui(set_webcam_image, img)
            toc("photoimage")
        finally:
            if cap is not None:
                tic("release")
                try:
                    cap.release()
                except Exception:
                    pass
                toc("release")
            ui(scan_button.config, state="normal")
            if times:
                times_ms = {k: int(v * 1000) for k, v in times.items()}
                order = [
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
                    "release",
                ]
                summary = "Perf:" + ", ".join(
                    f"{k}={times_ms[k]}ms" for k in order if k in times_ms
                )
                try:
                    ui(recognition.insert, "end", summary)
                except Exception:
                    pass
                print("Perf details (ms):", times_ms)

    threading.Thread(target=stream, daemon=True).start()