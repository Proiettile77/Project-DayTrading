import pandas as pd
import pytz

def ensure_tz_index(df: pd.DataFrame, tz: str):
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be DatetimeIndex")
    if df.index.tz is None:
        df = df.tz_localize("UTC")
    return df.tz_convert(tz)

def filter_session(df, session_start: str, session_end: str):
    # session_* as "HH:MM", in df.index tz
    s_h, s_m = map(int, session_start.split(":"))
    e_h, e_m = map(int, session_end.split(":"))
    t = df.index
    mask = (t.hour > s_h) | ((t.hour == s_h) & (t.minute >= s_m))
    mask &= (t.hour < e_h) | ((t.hour == e_h) & (t.minute <= e_m))
    return df[mask]
