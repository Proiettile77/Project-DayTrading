"""Credential storage utilities for multiple providers with non-destructive `.env` merge."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

import keyring
from dotenv import dotenv_values

try:  # tomllib is builtin on Python >=3.11
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


PROJECT_ROOT = Path(os.getenv("APP_ROOT", Path(__file__).resolve().parents[2]))
STREAMLIT_DIR = PROJECT_ROOT / ".streamlit"
SECRETS_FILE = STREAMLIT_DIR / "secrets.toml"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_BAK = PROJECT_ROOT / ".env.bak"


# Mapping provider -> env variable names & defaults
PROVIDER_VARS: Dict[str, Dict[str, str]] = {
    "alpaca": {
        "key": "APCA_API_KEY_ID",
        "secret": "APCA_API_SECRET_KEY",
        "base_url": "APCA_API_BASE_URL",
        "default_base_url": "https://paper-api.alpaca.markets",
    },
    "oanda": {
        "key": "OANDA_API_KEY",
        "secret": "OANDA_ACCOUNT_ID",
        "base_url": "OANDA_API_BASE_URL",
        "default_base_url": "https://api-fxpractice.oanda.com",
    },
    "binance": {
        "key": "BINANCE_API_KEY",
        "secret": "BINANCE_API_SECRET",
        "base_url": "BINANCE_API_BASE_URL",
        "default_base_url": "https://testnet.binance.vision",
    },
}


_CURRENT_BACKEND: Dict[str, Optional[str]] = {}


def _vars(provider: str) -> Dict[str, str]:
    if provider not in PROVIDER_VARS:
        raise ValueError(f"Unsupported provider {provider}")
    return PROVIDER_VARS[provider]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _creds_ok(creds: Dict[str, str]) -> bool:
    return bool(creds.get("key") and creds.get("secret"))


def _load_from_env(provider: str) -> Optional[Dict[str, str]]:
    names = _vars(provider)
    key = os.getenv(names["key"])
    secret = os.getenv(names["secret"])
    base = os.getenv(names["base_url"]) or names["default_base_url"]
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def _load_from_secrets(provider: str) -> Optional[Dict[str, str]]:
    if not SECRETS_FILE.exists() or tomllib is None:
        return None
    try:
        with open(SECRETS_FILE, "rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return None
    names = _vars(provider)
    key = data.get(names["key"])
    secret = data.get(names["secret"])
    base = data.get(names["base_url"]) or names["default_base_url"]
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def _load_from_keyring(provider: str) -> Optional[Dict[str, str]]:
    try:
        raw = keyring.get_password(provider, "default")
    except Exception:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    names = _vars(provider)
    key = data.get("key")
    secret = data.get("secret")
    base = data.get("base_url") or names["default_base_url"]
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def _load_from_env_file(provider: str) -> Optional[Dict[str, str]]:
    if not ENV_FILE.exists():
        return None
    data = dotenv_values(ENV_FILE)
    names = _vars(provider)
    key = data.get(names["key"])
    secret = data.get(names["secret"])
    base = data.get(names["base_url"]) or names["default_base_url"]
    creds = {"key": key, "secret": secret, "base_url": base}
    return creds if _creds_ok(creds) else None


def load(provider: str) -> Dict[str, str]:
    for backend, loader in [
        ("env", _load_from_env),
        ("secrets", _load_from_secrets),
        ("keyring", _load_from_keyring),
        ("env_file", _load_from_env_file),
    ]:
        creds = loader(provider)
        if creds:
            _CURRENT_BACKEND[provider] = backend
            return creds
    _CURRENT_BACKEND[provider] = None
    names = _vars(provider)
    return {"key": "", "secret": "", "base_url": names["default_base_url"]}


def current_storage_backend(provider: str) -> Optional[str]:
    return _CURRENT_BACKEND.get(provider)


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


def _write_env_file(data: Dict[str, str]) -> None:
    existing: Dict[str, str] = {}
    if ENV_FILE.exists():
        ENV_BAK.write_text(ENV_FILE.read_text())
        existing = dotenv_values(ENV_FILE)
    existing.update(data)
    with open(ENV_FILE, "w", encoding="utf-8") as fh:
        for k, v in existing.items():
            if v is None:
                continue
            fh.write(f"{k}={v}\n")


def save(provider: str, target: str, key: str, secret: str, base_url: str) -> None:
    names = _vars(provider)
    if target == "secrets":
        STREAMLIT_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        if SECRETS_FILE.exists() and tomllib is not None:
            try:
                with open(SECRETS_FILE, "rb") as fh:
                    data = tomllib.load(fh)
            except Exception:
                data = {}
        data.update(
            {
                names["key"]: key,
                names["secret"]: secret,
                names["base_url"]: base_url,
            }
        )
        with open(SECRETS_FILE, "w", encoding="utf-8") as fh:
            for k, v in data.items():
                fh.write(f"{k}='{v}'\n")
    elif target == "keyring":
        payload = json.dumps({"key": key, "secret": secret, "base_url": base_url})
        keyring.set_password(provider, "default", payload)
    elif target == "env_file":
        _write_env_file(
            {names["key"]: key, names["secret"]: secret, names["base_url"]: base_url}
        )
    else:
        raise ValueError(f"Unsupported target {target}")


# ---------------------------------------------------------------------------
# Deleters
# ---------------------------------------------------------------------------


def delete(provider: str, target: str) -> None:
    names = _vars(provider)
    if target == "secrets":
        if not SECRETS_FILE.exists() or tomllib is None:
            return
        try:
            with open(SECRETS_FILE, "rb") as fh:
                data = tomllib.load(fh)
        except Exception:
            return
        changed = False
        for k in (names["key"], names["secret"], names["base_url"]):
            if k in data:
                data.pop(k)
                changed = True
        if changed:
            with open(SECRETS_FILE, "w", encoding="utf-8") as fh:
                for k, v in data.items():
                    fh.write(f"{k}='{v}'\n")
    elif target == "keyring":
        try:
            keyring.delete_password(provider, "default")
        except Exception:
            pass
    elif target == "env_file":
        if not ENV_FILE.exists():
            return
        ENV_BAK.write_text(ENV_FILE.read_text())
        data = dotenv_values(ENV_FILE)
        for k in (names["key"], names["secret"], names["base_url"]):
            data.pop(k, None)
        with open(ENV_FILE, "w", encoding="utf-8") as fh:
            for k, v in data.items():
                if v is None:
                    continue
                fh.write(f"{k}={v}\n")
    else:
        raise ValueError(f"Unsupported target {target}")


__all__ = [
    "load",
    "save",
    "delete",
    "current_storage_backend",
    "PROVIDER_VARS",
]

