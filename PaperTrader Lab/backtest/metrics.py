import pandas as pd
import numpy as np

def equity_to_metrics(equity: pd.Series, rf_daily: float = 0.0):
    # equity: portfolio value over time (index datetime)
    ret = equity.pct_change().dropna()
    # CAGR
    if len(equity) < 2:
        return {}
    days = (equity.index[-1] - equity.index[0]).days or 1
    years = days / 365.25
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1/years) - 1 if years>0 else np.nan
    # Sharpe (daily)
    excess = ret - rf_daily
    sharpe = np.nan
    if excess.std(ddof=1) > 0:
        sharpe = (excess.mean() / excess.std(ddof=1)) * np.sqrt(252)
    # Sortino
    downside = excess[excess < 0]
    sortino = np.nan
    if downside.std(ddof=1) > 0:
        sortino = (excess.mean() / downside.std(ddof=1)) * np.sqrt(252)
    # Max DD & Calmar
    cum = (1 + ret).cumprod()
    peak = cum.cummax()
    dd = cum/peak - 1
    maxdd = dd.min()
    calmar = np.nan if maxdd == 0 else (cagr / abs(maxdd)) if pd.notna(cagr) else np.nan
    exposure = 1.0  # placeholder; for full accuracy, compute from trades
    return dict(
        CAGR=cagr, Sharpe=sharpe, Sortino=sortino, MaxDrawdown=maxdd, Calmar=calmar,
        Exposure=exposure, AvgDailyRet=ret.mean(), VolDaily=ret.std(ddof=1)
    )
