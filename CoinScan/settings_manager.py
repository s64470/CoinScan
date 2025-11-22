# -*- coding: utf-8 -*-
"""Manage loading and saving application settings with safe, atomic writes."""
from pathlib import Path
import json
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "language": "en",
    "webcam_size": "small",
    "high_contrast": False,
    "font_size": 14,
}


def _default_settings_path() -> Path:
    """Resolve the settings file path.

    - Honor COINSCAN_SETTINGS env var (file or directory).
    - Otherwise use platform-appropriate config directory.
    - Fall back to CWD if directory creation fails.
    """
    env = os.getenv("COINSCAN_SETTINGS")
    if env:
        p = Path(env)
        # If env points to an existing directory, use a filename inside it.
        if p.is_dir():
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.debug(
                    "Failed to ensure COINSCAN_SETTINGS directory exists: %s",
                    p,
                    exc_info=True,
                )
            return p / "coinscan_settings.json"

        # Treat env as a file path (ensure parent exists).
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.debug(
                "Failed to create parent for COINSCAN_SETTINGS file: %s",
                p.parent,
                exc_info=True,
            )
        return p

    # No env var: choose platform-appropriate config location.
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", str(Path.home())))
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))

    cfg_dir = base / "CoinScan"
    try:
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / "coinscan_settings.json"
    except Exception:
        logger.debug(
            "Failed to create config directory %s, falling back to cwd",
            cfg_dir,
            exc_info=True,
        )
        return Path.cwd() / "coinscan_settings.json"


SETTINGS_FILE: Path = _default_settings_path()


def _validate_and_merge(data: object) -> dict:
    """Return a merged settings dict: defaults + validated incoming values.

    Unknown keys from the incoming data are preserved. For known keys, the
    incoming value is accepted only if its type exactly matches the default's
    type; otherwise the default value is used and a debug message is emitted.
    """
    if not isinstance(data, dict):
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    # Preserve unknown keys provided by the user.
    merged.update({k: v for k, v in data.items() if k not in DEFAULT_SETTINGS})

    for key, default_value in DEFAULT_SETTINGS.items():
        if key in data:
            incoming = data[key]
            # Use exact type match to avoid accepting e.g. bool where int is expected.
            if type(incoming) is type(default_value):
                merged[key] = incoming
            else:
                merged[key] = default_value
                logger.debug(
                    "Setting %s has wrong type (%s) - using default (%s)",
                    key,
                    type(incoming),
                    type(default_value),
                )
    return merged


def load_settings() -> dict:
    """Load settings from disk and return validated settings, or defaults on error."""
    try:
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_and_merge(data)
    except Exception:
        logger.exception("Failed to load settings, using defaults")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Persist settings to disk using an atomic replace via a temporary file."""
    if not isinstance(settings, dict):
        raise TypeError("settings must be a dict")

    to_save = _validate_and_merge(settings)

    # Ensure directory exists before writing.
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        logger.debug(
            "Failed to ensure settings directory exists: %s",
            SETTINGS_FILE.parent,
            exc_info=True,
        )

    tmp_path = None
    try:
        # Use NamedTemporaryFile(delete=False) to allow safe replace on Windows.
        with tempfile.NamedTemporaryFile(
            prefix=SETTINGS_FILE.name + ".",
            suffix=".tmp",
            dir=str(SETTINGS_FILE.parent),
            mode="w",
            encoding="utf-8",
            delete=False,
        ) as tmp_fp:
            json.dump(to_save, tmp_fp, indent=2, ensure_ascii=False)
            tmp_fp.flush()
            os.fsync(tmp_fp.fileno())
            tmp_path = Path(tmp_fp.name)

        # Atomically replace the target file with the temp file.
        os.replace(str(tmp_path), str(SETTINGS_FILE))
    except Exception:
        logger.exception("Failed to save settings")
        # Best-effort cleanup of temporary file.
        try:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            logger.debug(
                "Failed to remove temporary settings file: %s", tmp_path, exc_info=True
            )