"""OANDA provider plugin."""

from __future__ import annotations

from typing import Dict

import httpx

from .base import Provider


class OandaProvider(Provider):
    name = "oanda"

    def validate(self, creds: Dict[str, str]) -> None:
        super().validate(creds)
        url = f"{creds['base_url'].rstrip('/')}/v3/accounts"
        headers = {"Authorization": f"Bearer {creds['key']}"}
        try:
            resp = httpx.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:  # pragma: no cover - network errors
            raise ValueError(f"{e.response.status_code} {e.response.text}") from e
        except httpx.HTTPError as e:  # pragma: no cover - network errors
            raise ValueError(f"network error: {e}") from e


__all__ = ["OandaProvider"]

