#!/usr/bin/env python3
"""Securely configure the local Jev API key without printing it."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


DEFAULT_KEY_PATH = Path.home() / ".config/jev-decision/api_key"


class ConfigurationError(RuntimeError):
    pass


def clean_key(value: str) -> str:
    key = value.strip()
    if not key:
        raise ConfigurationError("The Jev API key cannot be empty.")
    if "\n" in key or "\r" in key:
        raise ConfigurationError("The Jev API key must be a single line.")
    return key


def save_api_key(value: str, key_path: Path = DEFAULT_KEY_PATH) -> Path:
    key = clean_key(value)
    key_path = key_path.expanduser()
    key_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(key_path.parent, 0o700)
    temporary = key_path.with_name(f".{key_path.name}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(key)
        os.replace(temporary, key_path)
        os.chmod(key_path, 0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return key_path


def check_configuration(key_path: Path = DEFAULT_KEY_PATH) -> dict[str, str]:
    environment_key = os.environ.get("JEV_DECISION_API_KEY", "").strip()
    if environment_key:
        clean_key(environment_key)
        return {"status": "ready", "source": "environment", "key_name": "JEV_DECISION_API_KEY"}
    key_path = key_path.expanduser()
    if not key_path.is_file():
        raise ConfigurationError(f"No Jev API key was found at {key_path}.")
    clean_key(key_path.read_text(encoding="utf-8"))
    permissions = stat.S_IMODE(key_path.stat().st_mode)
    if os.name != "nt" and permissions & 0o077:
        raise ConfigurationError(f"The Jev API key permissions are too broad ({permissions:03o}); expected 600.")
    result = {"status": "ready", "key_path": str(key_path)}
    if os.name != "nt":
        result["permissions"] = format(permissions, "03o")
    return result


def prompt_for_api_key() -> str:
    if sys.platform == "darwin":
        script = '''
set dialogResult to display dialog "Paste your Jev API key. It will be saved locally and will not be printed." default answer "" with hidden answer buttons {"Cancel", "Save"} default button "Save" cancel button "Cancel" with title "Configure Jev"
return text returned of dialogResult
'''
        completed = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise ConfigurationError("API key configuration was cancelled.")
        return completed.stdout
    if sys.stdin.isatty():
        return getpass.getpass("Paste your Jev API key: ")
    raise ConfigurationError("Run this script interactively to enter the API key securely.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Securely save or check the local Jev API key.")
    parser.add_argument("--check", action="store_true", help="Check the local key and permissions.")
    args = parser.parse_args()
    try:
        result = check_configuration() if args.check else {"status": "configured", "key_path": str(save_api_key(prompt_for_api_key()))}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ConfigurationError, OSError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
