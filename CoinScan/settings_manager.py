# -*- coding: utf-8 -*-
import json
import os
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default settings used when user settings are missing or invalid.
DEFAULT_SETTINGS = {
    "language": "en",
    "webcam_size": "small",
    "high_contrast": False,
    "font_size": 14,
}


def _default_settings_path() -> Path:
    # Determine the path for the settings file.
    # Respect COINSCAN_SETTINGS env var if set; it may point to a file or dir.
    env = os.getenv("COINSCAN_SETTINGS")
    if env:
        p = Path(env)
        if p.is_dir():
            # If env is a directory ensure it exists and use a default filename inside it.
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.debug(
                    "Failed to ensure COINSCAN_SETTINGS directory exists: %s",
                    p,
                    exc_info=True,
                )
            return p / "coinscan_settings.json"
        # If env points to a file, ensure parent directory exists and use that file.
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
        # Try to create the application config directory and return path inside it.
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / "coinscan_settings.json"
    except Exception:
        # If creation fails, fall back to current working directory.
        logger.debug(
            "Failed to create config directory %s, falling back to cwd",
            cfg_dir,
            exc_info=True,
        )
        return Path.cwd() / "coinscan_settings.json"


# Resolved file path used by load/save functions.
SETTINGS_FILE: Path = _default_settings_path()


def _validate_and_merge(data: object) -> dict:
    # Ensure incoming data is a dict and merge it with defaults.
    if not isinstance(data, dict):
        return DEFAULT_SETTINGS.copy()

    # Start with defaults. Keep any unknown keys from incoming data.
    merged = DEFAULT_SETTINGS.copy()
    merged.update({k: v for k, v in data.items() if k not in DEFAULT_SETTINGS})

    # For each known setting, validate its type and use either incoming or default.
    for k, default_value in DEFAULT_SETTINGS.items():
        if k in data:
            incoming = data[k]
            if type(incoming) is type(default_value):
                merged[k] = incoming
            else:
                # Type mismatch -> fall back to default and log debug info.
                merged[k] = default_value
                logger.debug(
                    "Setting %s has wrong type (%s) - using default (%s)",
                    k,
                    type(incoming),
                    type(default_value),
                )
    return merged


def load_settings() -> dict:
    # Load settings from disk if present. Return validated settings or defaults.
    try:
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_and_merge(data)
    except Exception:
        logger.exception("Failed to load settings, using defaults")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    # Persist settings to disk using an atomic replace via a temporary file.
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

    tmp_fp = None
    try:
        # Create a temp file in the same directory for atomic replace.
        fd, tmp_path = tempfile.mkstemp(
            prefix=SETTINGS_FILE.name + ".",
            suffix=".tmp",
            dir=str(SETTINGS_FILE.parent),
        )
        # Open file descriptor as a text file for JSON writing.
        tmp_fp = os.fdopen(fd, "w", encoding="utf-8")
        json.dump(to_save, tmp_fp, indent=2, ensure_ascii=False)
        tmp_fp.flush()
        # Ensure data is flushed to disk.
        os.fsync(tmp_fp.fileno())
        tmp_fp.close()
        tmp_fp = None
        # Atomically replace the target file with the temp file.
        os.replace(tmp_path, SETTINGS_FILE)
    except Exception:
        # On any error, log and try to clean up the temporary file/handle.
        logger.exception("Failed to save settings")
        try:
            if tmp_fp is not None:
                tmp_fp.close()
        except Exception:
            pass
        try:
            if "tmp_path" in locals() and Path(tmp_path).exists():
                Path(tmp_path).unlink()
        except Exception:
            logger.debug(
                "Failed to remove temporary settings file: %s",
                locals().get("tmp_path"),
                exc_info=True,
            )