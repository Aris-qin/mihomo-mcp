"""Configuration loading: YAML file + env vars overrides.

Order (highest priority first):
1. Environment variables (MIHOMO_HOST, MIHOMO_PORT, MIHOMO_SECRET, MIHOMO_TIMEOUT)
2. ~/.config/mihomo-mcp/config.yaml
3. Built-in defaults (host=127.0.0.1, port=9090, secret="", timeout=10)
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 9090,
    "secret": "",
    "timeout": 10,
}

CONFIG_PATH = Path(
    os.environ.get(
        "MIHOMO_MCP_CONFIG",
        Path.home() / ".config" / "mihomo-mcp" / "config.yaml",
    )
)


def _coerce_int(value: object, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def load_config() -> dict:
    """Load mihomo endpoint configuration."""
    cfg: dict = dict(DEFAULTS)

    if CONFIG_PATH.is_file():
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        mihomo = data.get("mihomo", {}) if isinstance(data, dict) else {}
        for key in DEFAULTS:
            if key in mihomo:
                cfg[key] = mihomo[key]

    if "MIHOMO_HOST" in os.environ:
        cfg["host"] = os.environ["MIHOMO_HOST"]
    if "MIHOMO_PORT" in os.environ:
        cfg["port"] = _coerce_int(os.environ["MIHOMO_PORT"], DEFAULTS["port"])
    if "MIHOMO_SECRET" in os.environ:
        cfg["secret"] = os.environ["MIHOMO_SECRET"]
    if "MIHOMO_TIMEOUT" in os.environ:
        cfg["timeout"] = _coerce_int(os.environ["MIHOMO_TIMEOUT"], DEFAULTS["timeout"])

    cfg["port"] = _coerce_int(cfg["port"], DEFAULTS["port"])
    cfg["timeout"] = _coerce_int(cfg["timeout"], DEFAULTS["timeout"])

    return cfg


def get_endpoint() -> tuple[str, int, str, int]:
    """Return (host, port, secret, timeout) tuple."""
    cfg = load_config()
    return cfg["host"], cfg["port"], cfg["secret"], cfg["timeout"]
