"""Utility per memorizzare le credenziali in modo sicuro e portabile."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

import keyring
from dotenv import dotenv_values, set_key

try:  # tomllib is builtin on Python >=3.11
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore

PROJECT_ROOT = Path(os.getenv("APP_ROOT", Path(__file__).resolve().parents[2]))
STREAMLIT_DIR = PROJECT_ROOT / ".streamlit"
SECRETS_FILE = STREAMLIT_DIR / "secrets.toml"
ENV_FILE = PROJECT_ROOT / ".env"


def _creds_ok(creds: Dict[str, str]) -> bool:
    return bool(creds.get("key") and creds.get("secret"))


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_from_env() -> Optional[Dict[str, str]]:
    key = os.getenv("APCA_API_KEY_ID")
    secret = os.getenv("APCA_API_SECRET_KEY")
    base = os.getenv("APCA_API_BASE_URL") or "https://paper-api.alpaca.markets"
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def load_from_secrets() -> Optional[Dict[str, str]]:
    if not SECRETS_FILE.exists() or tomllib is None:
        return None
    try:
        with open(SECRETS_FILE, "rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return None
    key = data.get("APCA_API_KEY_ID")
    secret = data.get("APCA_API_SECRET_KEY")
    base = data.get("APCA_API_BASE_URL") or "https://paper-api.alpaca.markets"
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def load_from_keyring() -> Optional[Dict[str, str]]:
    try:
        raw = keyring.get_password("alpaca", "default")
    except Exception:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    key = data.get("key")
    secret = data.get("secret")
    base = data.get("base_url") or "https://paper-api.alpaca.markets"
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def load_from_env_file() -> Optional[Dict[str, str]]:
    if not ENV_FILE.exists():
        return None
    data = dotenv_values(ENV_FILE)
    key = data.get("APCA_API_KEY_ID")
    secret = data.get("APCA_API_SECRET_KEY")
    base = data.get("APCA_API_BASE_URL") or "https://paper-api.alpaca.markets"
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_to_secrets(key: str, secret: str, base_url: str) -> None:
    STREAMLIT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "APCA_API_KEY_ID": key,
        "APCA_API_SECRET_KEY": secret,
        "APCA_API_BASE_URL": base_url,
    }
    with open(SECRETS_FILE, "w", encoding="utf-8") as fh:
        for k, v in data.items():
            fh.write(f"{k}='{v}'\n")


def write_to_keyring(key: str, secret: str, base_url: str) -> None:
    payload = json.dumps({"key": key, "secret": secret, "base_url": base_url})
    keyring.set_password("alpaca", "default", payload)


def write_to_env_file(key: str, secret: str, base_url: str) -> None:
    ENV_FILE.touch(exist_ok=True)
    set_key(ENV_FILE, "APCA_API_KEY_ID", key)
    set_key(ENV_FILE, "APCA_API_SECRET_KEY", secret)
    set_key(ENV_FILE, "APCA_API_BASE_URL", base_url)


# ---------------------------------------------------------------------------
# Deleters
# ---------------------------------------------------------------------------

def delete_secrets() -> None:
    if SECRETS_FILE.exists():
        SECRETS_FILE.unlink()


def delete_keyring() -> None:
    try:
        keyring.delete_password("alpaca", "default")
    except Exception:
        pass


def delete_env_file() -> None:
    if ENV_FILE.exists():
        ENV_FILE.unlink()


__all__ = [
    "load_from_env",
    "load_from_secrets",
    "load_from_keyring",
    "load_from_env_file",
    "write_to_secrets",
    "write_to_keyring",
    "write_to_env_file",
    "delete_secrets",
    "delete_keyring",
    "delete_env_file",
]

