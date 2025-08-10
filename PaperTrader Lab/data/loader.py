from __future__ import annotations
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
from utils.config import SETTINGS
from utils.tz import ensure_tz_index, filter_session
from utils.errors import ProviderError
from typing import List, Literal, Optional
import datetime as dt

# -------- Alpaca ----------
def _alpaca_timeframe(tf: str):
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    m = {"1m": (1, "Minute"), "5m": (5, "Minute"), "15m": (15, "Minute"),
         "1h": (1, "Hour"), "D": (1, "Day")}
    n, unit = m[tf]
    return TimeFrame(n, getattr(TimeFrameUnit, unit))

@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def _fetch_alpaca(symbols: List[str], tf: str, start: str, end: str, adjusted: bool=True) -> pd.DataFrame:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from utils.config import SETTINGS

    client = StockHistoricalDataClient(SETTINGS.alpaca_api_key, SETTINGS.alpaca_secret_key)

    feed = SETTINGS.alpaca_data_feed
    if feed not in {"iex", "sip"}:
        feed = "iex"  # fallback sicuro

    req = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=_alpaca_timeframe(tf),
        start=pd.Timestamp(start, tz="UTC"),
        end=pd.Timestamp(end, tz="UTC"),
        adjustment="split" if adjusted else "raw",
        feed=feed,  # <<<<<<<<<<<<<<  usa il feed gratuito
    )
    bars = client.get_stock_bars(req).df

    if bars.empty:
        raise ProviderError("Alpaca returned no data")
    # Normalize to single symbol columns via concat
    frames = []
    for s in symbols:
        df = bars.xs(s, level=0).rename(columns=str.lower)
        df = df[["open","high","low","close","volume"]]
        df["symbol"] = s
        frames.append(df)
    out = pd.concat(frames).sort_index()
    return out

# -------- Alpha Vantage ----------
@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def _fetch_alpha_vantage(symbols: List[str], tf: str, start: str, end: str, adjusted: bool=True) -> pd.DataFrame:
    import httpx, time
    key = SETTINGS.av_key
    if not key:
        raise ProviderError("Alpha Vantage key missing")
    frames = []
    for s in symbols:
        if tf in {"1m","5m","15m","1h"}:
            interval = {"1m":"1min","5m":"5min","15m":"15min","1h":"60min"}[tf]
            fn = "TIME_SERIES_INTRADAY"
            params = dict(function=fn, symbol=s, interval=interval, apikey=key, outputsize="full", datatype="json")
            url = "https://www.alphavantage.co/query"
            resp = httpx.get(url, params=params, timeout=30)
            resp.raise_for_status()
            js = resp.json()
            key_name = [k for k in js.keys() if "Time Series" in k]
            if not key_name: 
                raise ProviderError(f"Alpha Vantage error: {js.get('Note') or js.get('Error Message') or 'unknown'}")
            raw = pd.DataFrame(js[key_name[0]]).T
        else:
            fn = "TIME_SERIES_DAILY_ADJUSTED" if adjusted else "TIME_SERIES_DAILY"
            url = "https://www.alphavantage.co/query"
            params = dict(function=fn, symbol=s, apikey=key, outputsize="full", datatype="json")
            resp = httpx.get(url, params=params, timeout=30)
            resp.raise_for_status()
            js = resp.json()
            key_name = [k for k in js.keys() if "Time Series" in k][0]
            raw = pd.DataFrame(js[key_name]).T

        raw.index = pd.to_datetime(raw.index, utc=True)
        raw = raw.sort_index()
        # rename to OHLCV
        cols = {c:c.split(". ")[1] for c in raw.columns}
        raw = raw.rename(columns=cols)[["open","high","low","close","volume"]].astype(float)
        raw["symbol"] = s
        frames.append(raw.loc[start:end])
        time.sleep(1)  # be nice to rate limit 25/day
    return pd.concat(frames).sort_index()

def load_ohlcv(
    symbols: List[str],
    provider: Literal["alpaca","alphavantage"]="alpaca",
    timeframe: Literal["1m","5m","15m","1h","D"]="15m",
    start_date: str="2024-01-01",
    end_date: str|None=None,
    tz: str="America/New_York",
    session_filter_on: bool=False,
    session_start: str="09:30",
    session_end: str="16:00",
    adjusted: bool=True
) -> pd.DataFrame:
    """Return index tz-aware, columns: open,high,low,close,volume,symbol"""
    end_date = end_date or pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    if provider == "alpaca":
        df = _fetch_alpaca(symbols, timeframe, start_date, end_date, adjusted=adjusted)
    elif provider == "alphavantage":
        df = _fetch_alpha_vantage(symbols, timeframe, start_date, end_date, adjusted=adjusted)
    else:
        raise ProviderError(f"Unknown provider: {provider}")
    df = ensure_tz_index(df, tz)
    if session_filter_on:
        df = df.groupby("symbol", group_keys=False).apply(lambda d: filter_session(d, session_start, session_end))
    # sort columns order
    return df[["open","high","low","close","volume","symbol"]]
