"""Central configuration and credential management for multiple providers."""

from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

from pydantic_settings import BaseSettings

from .logging_json import get_logger
from . import secure_store
from .providers import PROVIDERS

log = get_logger("config")


CURRENT_BACKEND: Dict[str, Optional[str]] = {}


def load_credentials(provider: str) -> Dict[str, str]:
    """Load credentials for the given provider following precedence."""
    creds = secure_store.load(provider)
    CURRENT_BACKEND[provider] = secure_store.current_storage_backend(provider)
    log.info("credentials_loaded", extra={"provider": provider, "backend": CURRENT_BACKEND[provider]})
    return creds


def current_storage_backend(provider: str) -> Optional[str]:
    return CURRENT_BACKEND.get(provider)


def save_credentials(provider: str, target: str, key: str, secret: str, base_url: str) -> None:
    secure_store.save(provider, target, key, secret, base_url)
    log.info("credentials_saved", extra={"provider": provider, "backend": target})


def clear_credentials(provider: str, target: str) -> None:
    secure_store.delete(provider, target)
    log.info("credentials_cleared", extra={"provider": provider, "backend": target})


def test_credentials(provider: str, key: str, secret: str, base_url: str) -> Tuple[bool, str]:
    """Validate credentials using provider plugin."""
    try:
        PROVIDERS[provider].validate({"key": key, "secret": secret, "base_url": base_url})
        return True, ""
    except Exception as e:  # pragma: no cover - network or plugin errors
        msg = str(e)
        cause = getattr(e, "__cause__", None)
        if cause:
            msg = f"{msg} (caused by {cause})"
        return False, msg


def _as_bool(x: str, default: bool = False) -> bool:
    if x is None:
        return default
    return str(x).strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    """Application settings resolved from environment/.env."""

    default_engine: str = os.getenv("DEFAULT_ENGINE", "backtrader")
    default_data_provider: str = os.getenv("DEFAULT_DATA_PROVIDER", "alpaca")

    enable_alpaca: bool = _as_bool(os.getenv("ENABLE_ALPACA", "true"))
    enable_oanda: bool = _as_bool(os.getenv("ENABLE_OANDA", "false"))
    enable_binance: bool = _as_bool(os.getenv("ENABLE_BINANCE", "false"))

    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_base_url: str = secure_store.PROVIDER_VARS["alpaca"]["default_base_url"]

    oanda_api_key: str = ""
    oanda_secret_key: str = ""
    oanda_base_url: str = secure_store.PROVIDER_VARS["oanda"]["default_base_url"]

    binance_api_key: str = ""
    binance_secret_key: str = ""
    binance_base_url: str = secure_store.PROVIDER_VARS["binance"]["default_base_url"]

    class Config:
        env_file = secure_store.ENV_FILE


SETTINGS = Settings()


def reload_settings() -> None:
    for name in PROVIDERS:
        creds = load_credentials(name)
        setattr(SETTINGS, f"{name}_api_key", creds.get("key", ""))
        setattr(SETTINGS, f"{name}_secret_key", creds.get("secret", ""))
        setattr(SETTINGS, f"{name}_base_url", creds.get("base_url", ""))


# Load at import time
reload_settings()


__all__ = [
    "SETTINGS",
    "load_credentials",
    "save_credentials",
    "clear_credentials",
    "test_credentials",
    "current_storage_backend",
    "reload_settings",
    "PROVIDERS",
]

