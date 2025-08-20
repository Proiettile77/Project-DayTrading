"""Provider registry."""

from .alpaca import AlpacaProvider
from .oanda import OandaProvider
from .binance import BinanceProvider

PROVIDERS = {
    "alpaca": AlpacaProvider(),
    "oanda": OandaProvider(),
    "binance": BinanceProvider(),
}

__all__ = ["PROVIDERS"]

