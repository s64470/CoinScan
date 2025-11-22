from __future__ import annotations
import logging
import threading
from typing import Tuple, Callable, Any, Optional, List, Sequence

import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter, ImageDraw

from language import format_total, get_text

logger = logging.getLogger(__name__)

Size = Tuple[int, int]

# Hough / processing defaults
_HOUGH_DP = 1.2
_HOUGH_MIN_DIST = 30
_HOUGH_PARAM1 = 50
_HOUGH_PARAM2 = 16
_HOUGH_MIN_RADIUS = 15
_HOUGH_MAX_RADIUS = 90


def classify_coin(mean_hue: float, radius: int) -> Tuple[float, str, str]:
    """Classify a coin by mean hue and radius.

    Returns (value, label, colour_label).
    """
    if 18 < mean_hue < 35:
        colour_label = "Gold"
    elif 8 < mean_hue <= 18:
        colour_label = "Copper"
    else:
        colour_label = "Silver"

    # Size-based thresholds (largest-first)
    if colour_label == "Gold":
        if radius > 52:
            return 2.00, "2€", colour_label
        if radius > 32:
            return 0.50, "50ct", colour_label
        if radius > 27:
            return 0.20, "20ct", colour_label
        if radius > 22:
            return 0.10, "10ct", colour_label

    if colour_label == "Silver" and radius > 42:
        return 1.00, "1€", colour_label

    if colour_label == "Copper":
        if radius > 21:
            return 0.05, "5ct", colour_label
        if radius > 18:
            return 0.02, "2ct", colour_label
        if radius > 15:
            return 0.01, "1ct", colour_label

    return 0.00, "Unknown", colour_label


def centre_coins(
    circles: np.ndarray | Sequence[Tuple[float, float, float]],
    frame_shape: Tuple[int, int, int],
) -> List[Tuple[int, int, int]]:
    """Filter detected circles to those near the frame centre.

    Accepts HoughCircles output in either shape (1, N, 3) or (N, 3).
    Returns a list of (x, y, r) with ints.
    """
    if circles is None:
        return []

    arr = np.asarray(circles)

    # Normalize common (1, N, 3) -> (N, 3)
    if arr.ndim == 3 and arr.shape[0] == 1:
        arr = arr[0]

    # Safely coerce to integer coordinates
    try:
        arr = np.rint(arr).astype(int)
    except Exception:
        try:
            arr = np.array([[int(x), int(y), int(r)] for x, y, r in arr], dtype=int)
        except Exception:
            logger.exception("Failed to coerce circle coordinates to ints")
            return []

    height, width = frame_shape[:2]
    cx, cy = width // 2, height // 2
    tolx = int(width * 0.2)
    toly = int(height * 0.2)

    results: List[Tuple[int, int, int]] = []
    for x, y, r in arr:
        if abs(x - cx) <= tolx and abs(y - cy) <= toly:
            results.append((int(x), int(y), int(r)))

    return results


def update_recognition(
    scan_button: Any,
    recognition: Any,
    total_label: Any,
    webcam_label: Any,
    current_size: Size,
    current_lang: str,
    on_results: Optional[Callable[[List[Tuple[float, str]]], None]] = None,
) -> None:
    """Run a single-frame capture, classify any central coin and update UI.

    If `on_results` is provided it will be called on the UI thread with
    a list of (value, label) tuples for each detected coin.
    """
    # Best-effort: disable scan button immediately
    try:
        scan_button.config(state="disabled")
    except Exception:
        logger.debug("Failed to disable scan button", exc_info=True)

    def stream() -> None:
        def ui(callable_obj: Callable, *args, **kwargs) -> None:
            """Schedule a callable on the Tk main thread if possible, else run inline."""
            try:
                recognition.after(0, lambda: callable_obj(*args, **kwargs))
            except Exception:
                try:
                    callable_obj(*args, **kwargs)
                except Exception:
                    logger.debug("Failed to run UI callable", exc_info=True)

        def set_webcam_image(pil_img: Image.Image) -> None:
            """Set a PIL image onto the webcam_label while preventing GC."""
            try:
                imgtk = ImageTk.PhotoImage(image=pil_img)
                webcam_label.imgtk = imgtk  # keep reference to prevent GC
                webcam_label.configure(image=imgtk)
                try:
                    scan_button.config(text=get_text(current_lang, "rescan", "Rescan"))
                except Exception:
                    # Non-critical UI update
                    pass
            except Exception:
                logger.debug("Failed to set webcam image", exc_info=True)

        def compute_mean_hue_from_mask(
            frame_bgr: np.ndarray, mask: np.ndarray
        ) -> float:
            """Return mean hue for pixels inside mask (0/255) or 0.0 if none."""
            try:
                coin_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
                # Select hue values where mask is set
                coin_hue = coin_hsv[:, :, 0][mask == 255].astype(np.float64)
                return float(np.mean(coin_hue)) if coin_hue.size > 0 else 0.0
            except Exception:
                logger.debug("Failed to compute mean hue", exc_info=True)
                return 0.0

        def annotate_image(
            frame_rgb: np.ndarray, detected_circle: Tuple[int, int, int]
        ) -> Image.Image:
            """Return a PIL Image with blur-outside-coin and annotations applied."""
            img = Image.fromarray(
                cv2.resize(frame_rgb, current_size, interpolation=cv2.INTER_LINEAR)
            )
            try:
                orig_h, orig_w = frame_rgb.shape[:2]
                dst_w, dst_h = current_size
                sx = dst_w / orig_w
                sy = dst_h / orig_h
                scale = (sx + sy) / 2.0

                x_s = int(detected_circle[0] * sx)
                y_s = int(detected_circle[1] * sy)
                r_s = max(1, int(detected_circle[2] * scale))

                blur_radius = max(15, r_s // 2)
                # MedianFilter expects an odd integer size >= 3
                kernel = max(3, (int(blur_radius) // 2) * 2 + 1)
                blurred = img.filter(ImageFilter.MedianFilter(size=kernel))

                mask_img = Image.new("L", img.size, 0)
                draw_mask = ImageDraw.Draw(mask_img)
                bbox = (x_s - r_s, y_s - r_s, x_s + r_s, y_s + r_s)
                draw_mask.ellipse(bbox, fill=255)

                out = Image.composite(img, blurred, mask_img)

                draw = ImageDraw.Draw(out)
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
                return out
            except Exception:
                logger.debug("Failed during annotation/blur step", exc_info=True)
                return img

        cap: Optional[cv2.VideoCapture] = None
        try:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(current_size[0]))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(current_size[1]))

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
                dp=_HOUGH_DP,
                minDist=_HOUGH_MIN_DIST,
                param1=_HOUGH_PARAM1,
                param2=_HOUGH_PARAM2,
                minRadius=_HOUGH_MIN_RADIUS,
                maxRadius=_HOUGH_MAX_RADIUS,
            )

            ui(recognition.delete, 0, "end")
            total = 0.0
            results: List[Tuple[float, str]] = []
            detected_circle: Optional[Tuple[int, int, int]] = None

            if circles is not None:
                centered = centre_coins(circles, frame.shape)
                if centered:
                    # choose the largest detected central circle
                    x, y, r = max(centered, key=lambda c: c[2])

                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), int(r), 255, -1)
                    mean_hue = compute_mean_hue_from_mask(frame, mask)

                    value, label, _ = classify_coin(mean_hue, int(r))
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

            # Deliver results to caller or update total label
            if on_results is not None:
                try:
                    ui(on_results, results)
                except Exception:
                    logger.debug("Failed to call on_results", exc_info=True)
            else:
                ui(total_label.config, text=format_total(current_lang, total))

            # Prepare display image and push to UI
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if detected_circle is not None:
                img = annotate_image(frame_rgb, detected_circle)
            else:
                img = Image.fromarray(
                    cv2.resize(frame_rgb, current_size, interpolation=cv2.INTER_LINEAR)
                )

            ui(set_webcam_image, img)
        except Exception:
            logger.exception("Unexpected error in recognition stream")
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    logger.debug("Failed to release camera", exc_info=True)
            try:
                ui(scan_button.config, state="normal")
            except Exception:
                logger.debug("Failed to re-enable scan button", exc_info=True)

    threading.Thread(target=stream, daemon=True).start()