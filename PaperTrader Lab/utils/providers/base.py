"""Base provider interface."""

from __future__ import annotations

from typing import Dict, List


class Provider:
    """Simple provider plugin interface."""

    name: str = ""

    def get_required_fields(self) -> List[str]:
        return ["key", "secret", "base_url"]

    def validate(self, creds: Dict[str, str]) -> None:
        """Raise an exception if credentials are invalid."""
        if not creds.get("key") or not creds.get("secret"):
            raise ValueError("missing credentials")

    def build_client(self, creds: Dict[str, str]):  # pragma: no cover - placeholder
        raise NotImplementedError


__all__ = ["Provider"]

