"""Configuration loading helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


@lru_cache(maxsize=None)
def load_config(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if path.exists():
        return _read_json(path)

    package_root = resources.files("emotor_studio")
    fallback = package_root.joinpath("configs", name)
    with fallback.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def load_signals() -> list[dict[str, Any]]:
    return list(load_config("signals.json").get("signals", []))


def load_parameters() -> list[dict[str, Any]]:
    return list(load_config("parameters.json").get("parameters", []))


def load_fault_codes() -> list[dict[str, Any]]:
    return list(load_config("fault_codes.json").get("faults", []))


def load_commands() -> list[dict[str, Any]]:
    return list(load_config("commands.json").get("commands", []))
