import pandas as pd
from backtest.metrics import equity_to_metrics

def test_equity_metrics_basic():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    # Generate an equity curve with a small daily gain.
    # range objects cannot be used directly as an exponent with a float,
    # so compute each step explicitly.
    equity = pd.Series(
        [100000 * (1 + 0.001) ** i for i in range(10)], index=idx
    )
    m = equity_to_metrics(equity)
    assert "CAGR" in m and m["CAGR"] is not None
