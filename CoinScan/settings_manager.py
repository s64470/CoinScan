# -*- coding: utf-8 -*-

from pathlib import Path
import json
import logging
import os
import tempfile
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS: Dict[str, Any] = {
    "language": "en",
    "webcam_size": "small",
    "high_contrast": False,
    "font_size": 14,
}

__all__ = ("load_settings", "save_settings", "SETTINGS_FILE", "DEFAULT_SETTINGS")


def _default_settings_path() -> Path:
    env = os.getenv("COINSCAN_SETTINGS")
    if env:
        p = Path(env)
        if p.is_dir():
            return p / "coinscan_settings.json"
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.debug(
                "Failed to create parent for COINSCAN_SETTINGS file: %s",
                p.parent,
                exc_info=True,
            )
        return p

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


def _same_type(value: Any, prototype: Any) -> bool:
    if isinstance(prototype, bool):
        return isinstance(value, bool)
    return type(value) is type(prototype)


def _validate_and_merge(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return DEFAULT_SETTINGS.copy()

    merged: Dict[str, Any] = DEFAULT_SETTINGS.copy()
    unknown_items = {k: v for k, v in data.items() if k not in DEFAULT_SETTINGS}
    merged.update(unknown_items)

    for key, default_value in DEFAULT_SETTINGS.items():
        if key in data:
            incoming = data[key]
            if _same_type(incoming, default_value):
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


def load_settings() -> Dict[str, Any]:
    try:
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_and_merge(data)
    except Exception:
        logger.exception("Failed to load settings, using defaults")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> None:
    if not isinstance(settings, dict):
        raise TypeError("settings must be a dict")

    to_save = _validate_and_merge(settings)

    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        logger.debug(
            "Failed to ensure settings directory exists: %s",
            SETTINGS_FILE.parent,
            exc_info=True,
        )

    tmp_path: Path | None = None
    try:
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

        os.replace(str(tmp_path), str(SETTINGS_FILE))
        tmp_path = None
    except Exception:
        logger.exception("Failed to save settings")

        try:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            logger.debug(
                "Failed to remove temporary settings file: %s", tmp_path, exc_info=True
            )