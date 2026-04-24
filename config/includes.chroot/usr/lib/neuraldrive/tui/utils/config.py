from __future__ import annotations

import os
import subprocess
from typing import Any

import yaml

PERSISTENT_CONFIG = "/var/lib/neuraldrive/config/config.yaml"
OVERLAY_CONFIG = "/etc/neuraldrive/config.yaml"


def _config_path() -> str:
    persistent_dir = os.path.dirname(PERSISTENT_CONFIG)
    if os.path.isdir(persistent_dir) and os.access(persistent_dir, os.W_OK):
        return PERSISTENT_CONFIG
    return OVERLAY_CONFIG


def load() -> dict[str, Any]:
    for path in (PERSISTENT_CONFIG, OVERLAY_CONFIG):
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except (OSError, yaml.YAMLError):
                continue
    return {}


def save(data: dict[str, Any]) -> str | None:
    path = _config_path()
    content = yaml.dump(data, default_flow_style=False, sort_keys=False)
    try:
        mkdir_proc = subprocess.run(
            ["sudo", "mkdir", "-p", os.path.dirname(path)],
            capture_output=True,
            timeout=5,
        )
        if mkdir_proc.returncode != 0:
            return f"Failed to create dir for {path}: {mkdir_proc.stderr.decode().strip()}"
        proc = subprocess.run(
            ["sudo", "tee", path],
            input=content.encode(),
            capture_output=True,
            timeout=5,
        )
        if proc.returncode != 0:
            return f"Failed to write {path}: {proc.stderr.decode().strip()}"
        chmod_proc = subprocess.run(
            ["sudo", "chmod", "0644", path],
            capture_output=True,
            timeout=5,
        )
        if chmod_proc.returncode != 0:
            return f"Failed to chmod {path}: {chmod_proc.stderr.decode().strip()}"
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return f"Failed to write {path}: {e}"


def get(key: str, default: Any = None) -> Any:
    data = load()
    keys = key.split(".")
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k, default)
        else:
            return default
    return data


def set_key(key: str, value: Any) -> str | None:
    data = load()
    keys = key.split(".")
    target = data
    for k in keys[:-1]:
        if k not in target or not isinstance(target[k], dict):
            target[k] = {}
        target = target[k]
    target[keys[-1]] = value
    return save(data)
