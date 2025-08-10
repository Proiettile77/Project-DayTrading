import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _as_bool(x: str, default=False):
    if x is None:
        return default
    return str(x).strip().lower() in {"1", "true", "yes", "on"}

@dataclass
class Settings:
    default_engine: str = os.getenv("DEFAULT_ENGINE", "backtrader")
    default_data_provider: str = os.getenv("DEFAULT_DATA_PROVIDER", "alpaca")

    enable_alpaca: bool = _as_bool(os.getenv("ENABLE_ALPACA", "true"))
    enable_oanda: bool  = _as_bool(os.getenv("ENABLE_OANDA", "false"))
    enable_binance: bool= _as_bool(os.getenv("ENABLE_BINANCE", "false"))

    # Alpaca
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "")
    alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    alpaca_data_base_url: str = os.getenv("ALPACA_DATA_BASE_URL", "https://data.alpaca.markets")
    alpaca_data_feed: str = os.getenv("ALPACA_DATA_FEED", "iex").lower()


    # Alpha Vantage
    av_key: str = os.getenv("ALPHAVANTAGE_API_KEY", "")

SETTINGS = Settings()
