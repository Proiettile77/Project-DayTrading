import backtrader as bt

class EmaAtrStrategy(bt.Strategy):
    params = dict(
        ema_fast=12,
        ema_slow=26,
        atr_period=14,
        stop_mode="atr",   # "atr" or "percent"
        atr_mult_sl=2.0,
        atr_mult_tp=3.0,
        sl_pct=0.01,       # used if stop_mode="percent"
        tp_pct=0.02,
        time_in_market_max=None,  # bars
    )

    def __init__(self):
        self.ema_fast = bt.ind.EMA(self.data.close, period=self.p.ema_fast)
        self.ema_slow = bt.ind.EMA(self.data.close, period=self.p.ema_slow)
        self.crossover = bt.ind.CrossOver(self.ema_fast, self.ema_slow)
        self.atr = bt.ind.ATR(self.data, period=self.p.atr_period)
        self.order = None
        self.bars_in_trade = 0

    def next(self):
        if self.order:
            return

        if self.position:
            self.bars_in_trade += 1
            # time stop
            if self.p.time_in_market_max and self.bars_in_trade >= self.p.time_in_market_max:
                self.close()
            return

        # Entry: fast crosses above slow -> long (flat->long only)
        if self.crossover > 0:
            # Determine SL/TP
            price = self.data.close[0]
            if self.p.stop_mode == "atr":
                sl = price - self.p.atr_mult_sl * float(self.atr[0])
                tp = price + self.p.atr_mult_tp * float(self.atr[0])
            else:
                sl = price * (1 - self.p.sl_pct)
                tp = price * (1 + self.p.tp_pct)

            # Bracket order: market entry + OCO stop/take
            self.order = self.buy_bracket(limitprice=tp, stopprice=sl)
            self.bars_in_trade = 0

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
