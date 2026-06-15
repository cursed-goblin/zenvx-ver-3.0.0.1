#!/usr/bin/env python3
"""macprlandd scaffold.

This is intentionally minimal: it defines the config locations and the internal
interfaces that will be implemented next.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import yaml

CONFIG_DIR = Path.home() / ".config" / "macprland"
CONFIG_FILE = CONFIG_DIR / "config.yml"
RULES_FILE = CONFIG_DIR / "rules.yml"
SCRIPTS_DIR = CONFIG_DIR / "scripts"


@dataclass
class Config:
    raw: dict


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_config() -> Config:
    return Config(raw=load_yaml(CONFIG_FILE))


def load_rules() -> dict:
    return load_yaml(RULES_FILE)


def main() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    rules = load_rules()

    print("macprlandd scaffold running")
    print("config loaded keys:", list(cfg.raw.keys()))
    print("rules loaded keys:", list(rules.keys()) if isinstance(rules, dict) else type(rules))

    # TODO:
    # - connect to DBus io.zenvx.Macprland
    # - apply rules on WindowCreated
    # - implement file watchers + live reload
    # - implement Lua runtime and provider plugins

    while True:
        time.sleep(5)


if __name__ == "__main__":
    main()
