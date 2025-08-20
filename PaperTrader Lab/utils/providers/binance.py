"""Binance provider plugin."""

from __future__ import annotations

from typing import Dict

import hashlib
import hmac
import time
import httpx

from .base import Provider


class BinanceProvider(Provider):
    name = "binance"

    def validate(self, creds: Dict[str, str]) -> None:
        super().validate(creds)
        timestamp = int(time.time() * 1000)
        query = f"timestamp={timestamp}"
        signature = hmac.new(creds["secret"].encode(), query.encode(), hashlib.sha256).hexdigest()
        url = f"{creds['base_url'].rstrip('/')}/api/v3/account?{query}&signature={signature}"
        headers = {"X-MBX-APIKEY": creds["key"]}
        try:
            resp = httpx.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:  # pragma: no cover - network errors
            raise ValueError(f"{e.response.status_code} {e.response.text}") from e
        except httpx.HTTPError as e:  # pragma: no cover - network errors
            raise ValueError(f"network error: {e}") from e


__all__ = ["BinanceProvider"]

