import pandas as pd
from backtest.metrics import equity_to_metrics

def test_equity_metrics_basic():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    equity = pd.Series(100000 * (1 + 0.001) ** range(10), index=idx)
    m = equity_to_metrics(equity)
    assert "CAGR" in m and m["CAGR"] is not None
