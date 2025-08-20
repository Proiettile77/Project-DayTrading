"""OANDA provider plugin."""

from __future__ import annotations

from typing import Dict

from .base import Provider


class OandaProvider(Provider):
    name = "oanda"

    def validate(self, creds: Dict[str, str]) -> None:  # pragma: no cover - trivial
        super().validate(creds)


__all__ = ["OandaProvider"]

