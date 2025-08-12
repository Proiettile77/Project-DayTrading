"""Configurazioni e gestione credenziali Alpaca."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .logging_json import get_logger
from . import secure_store

log = get_logger("config")

CURRENT_BACKEND: Optional[str] = None


def load_credentials() -> Dict[str, str]:
    """Carica le credenziali seguendo la precedence richiesta."""
    global CURRENT_BACKEND
    for backend, loader in [
        ("env", secure_store.load_from_env),
        ("secrets", secure_store.load_from_secrets),
        ("keyring", secure_store.load_from_keyring),
        ("env_file", secure_store.load_from_env_file),
    ]:
        creds = loader()
        if creds:
            CURRENT_BACKEND = backend
            log.info("credentials_loaded", extra={"backend": backend})
            return creds
    CURRENT_BACKEND = None
    log.info("credentials_missing")
    return {"key": "", "secret": "", "base_url": "https://paper-api.alpaca.markets"}


def current_storage_backend() -> Optional[str]:
    return CURRENT_BACKEND


def save_credentials(target: str, key: str, secret: str, base_url: str) -> None:
    writers = {
        "secrets": secure_store.write_to_secrets,
        "keyring": secure_store.write_to_keyring,
        "env_file": secure_store.write_to_env_file,
    }
    if target not in writers:
        raise ValueError(f"Unsupported target {target}")
    writers[target](key, secret, base_url)
    log.info("credentials_saved", extra={"backend": target})


def clear_credentials(target: str) -> None:
    deleters = {
        "secrets": secure_store.delete_secrets,
        "keyring": secure_store.delete_keyring,
        "env_file": secure_store.delete_env_file,
    }
    if target in deleters:
        deleters[target]()
        log.info("credentials_cleared", extra={"backend": target})


def test_alpaca_credentials(key: str, secret: str, base_url: str) -> Tuple[bool, str]:
    """Prova una chiamata "whoami" per verificare le credenziali."""
    try:
        from alpaca.trading.client import TradingClient

        client = TradingClient(
            key,
            secret,
            paper="paper" in base_url,
            url_override=base_url,
        )
        client.get_account()
        return True, ""
    except Exception as e:  # pragma: no cover - network errors mocked nei test
        return False, str(e)


def _as_bool(x: str, default=False):
    if x is None:
        return default
    return str(x).strip().lower() in {"1", "true", "yes", "on"}


def _build_settings(creds: Dict[str, str]):
    @dataclass
    class Settings:
        default_engine: str = os.getenv("DEFAULT_ENGINE", "backtrader")
        default_data_provider: str = os.getenv("DEFAULT_DATA_PROVIDER", "alpaca")

        enable_alpaca: bool = _as_bool(os.getenv("ENABLE_ALPACA", "true"))
        enable_oanda: bool = _as_bool(os.getenv("ENABLE_OANDA", "false"))
        enable_binance: bool = _as_bool(os.getenv("ENABLE_BINANCE", "false"))

        alpaca_api_key: str = creds.get("key", "")
        alpaca_secret_key: str = creds.get("secret", "")
        alpaca_base_url: str = creds.get("base_url", "https://paper-api.alpaca.markets")
        alpaca_data_base_url: str = os.getenv("ALPACA_DATA_BASE_URL", "https://data.alpaca.markets")
        alpaca_data_feed: str = os.getenv("ALPACA_DATA_FEED", "iex").lower()

        av_key: str = os.getenv("ALPHAVANTAGE_API_KEY", "")

    return Settings()


SETTINGS = _build_settings(load_credentials())


def reload_settings() -> None:
    creds = load_credentials()
    SETTINGS.alpaca_api_key = creds.get("key", "")
    SETTINGS.alpaca_secret_key = creds.get("secret", "")
    SETTINGS.alpaca_base_url = creds.get("base_url", "https://paper-api.alpaca.markets")


__all__ = [
    "SETTINGS",
    "load_credentials",
    "save_credentials",
    "clear_credentials",
    "test_alpaca_credentials",
    "current_storage_backend",
    "reload_settings",
]

