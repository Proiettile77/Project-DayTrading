from backtest.engine import PercentRiskSizer
import backtrader as bt

def test_sizer_min_size():
    s = PercentRiskSizer(risk_per_trade=0.01, min_size=1)
    # Cash 100k, price 1M -> size should be min_size
    class Dummy: pass
    data = Dummy(); data.close = [1_000_000]
    size = s._getsizing(None, 100_000, data, True)
    assert size == 1
