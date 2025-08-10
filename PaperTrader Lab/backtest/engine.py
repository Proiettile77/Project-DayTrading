from __future__ import annotations
import backtrader as bt
import pandas as pd
from typing import Dict, Any, Optional
from strategies.ema_atr import EmaAtrStrategy
from backtest.metrics import equity_to_metrics

class PercentRiskSizer(bt.Sizer):
    params = dict(risk_per_trade=0.01, min_size=1)
    def _getsizing(self, comminfo, cash, data, isbuy):
        price = data.close[0]
        risk_cash = cash * self.p.risk_per_trade
        size = int(max(self.p.min_size, risk_cash // price))
        return size

def df_to_btfeed(df: pd.DataFrame):
    # expects single symbol OHLCV
    data = df[["open","high","low","close","volume"]].copy()
    data.columns = ["open","high","low","close","volume"]
    data_bt = bt.feeds.PandasData(dataname=data)
    return data_bt

def run_backtest(df: pd.DataFrame, cash: float, commission: float,
                 slippage_bps: float, sizer_kwargs: Dict[str, Any],
                 strategy_params: Dict[str, Any]) -> Dict[str, Any]:
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)  # e.g., 0.001 = 10 bps
    if slippage_bps:
        cerebro.broker.set_slippage_perc(perc=slippage_bps/1e4, slip_open=True, slip_limit=True, slip_match=True)

    # split per symbol; run portfolio by summing broker value at the end (sequential for MVP)
    results = []
    equity_curves = []

    for sym, sdf in df.groupby("symbol"):
        dfeed = df_to_btfeed(sdf.droplevel("symbol", axis=0) if isinstance(sdf.index, pd.MultiIndex) else sdf)
        cerebro_sym = bt.Cerebro(stdstats=False)
        cerebro_sym.broker.setcash(cash/len(df["symbol"].unique()))
        cerebro_sym.broker.setcommission(commission=commission)
        if slippage_bps:
            cerebro_sym.broker.set_slippage_perc(perc=slippage_bps/1e4)

        cerebro_sym.adddata(dfeed, name=sym)
        cerebro_sym.addsizer(PercentRiskSizer, **sizer_kwargs)
        cerebro_sym.addstrategy(EmaAtrStrategy, **strategy_params)

        # Analyzers
        cerebro_sym.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro_sym.addanalyzer(bt.analyzers.DrawDown, _name='dd')
        cerebro_sym.addanalyzer(bt.analyzers.TimeReturn, _name='ret', timeframe=bt.TimeFrame.Days)
        cerebro_sym.addobserver(bt.observers.Broker)
        cerebro_sym.addobserver(bt.observers.Trades)

        runstrat = cerebro_sym.run(maxcpus=1)[0]

        # Build equity curve from broker value over time
        # Backtrader doesn't expose broker series directly; approximate via returns
        ret = pd.Series(runstrat.analyzers.ret.get_analysis())
        equity = (1 + ret).cumprod()
        equity.index = pd.to_datetime(equity.index)
        equity_curves.append(equity.rename(sym))

        dd = runstrat.analyzers.dd.get_analysis()
        sh = runstrat.analyzers.sharpe.get_analysis()
        res = dict(symbol=sym,
                   sharpe=sh.get('sharperatio', None),
                   maxdd=dd.get('max', {}).get('drawdown', None))
        results.append(res)

    # combine equity curves (simple average notional)
    equity_df = pd.concat(equity_curves, axis=1).dropna()
    equity_port = equity_df.mean(axis=1)
    metrics = equity_to_metrics(equity_port)

    return dict(equity=equity_port, per_symbol=results, metrics=metrics)
