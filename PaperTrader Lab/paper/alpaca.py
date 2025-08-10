from __future__ import annotations
from typing import Dict, Any
from utils.config import SETTINGS
from utils.errors import ProviderError

def _trading_client():
    from alpaca.trading.client import TradingClient
    if not SETTINGS.alpaca_api_key or not SETTINGS.alpaca_secret_key:
        raise ProviderError("Missing Alpaca API keys")
    return TradingClient(SETTINGS.alpaca_api_key, SETTINGS.alpaca_secret_key, paper=True)

def account():
    tc = _trading_client()
    acc = tc.get_account()
    return {"id": acc.id, "status": acc.status, "cash": float(acc.cash), "portfolio_value": float(acc.portfolio_value)}

def positions():
    tc = _trading_client()
    pos = tc.get_all_positions()
    rows = []
    for p in pos:
        rows.append(dict(symbol=p.symbol, qty=float(p.qty), avg_entry=float(p.avg_entry_price),
                         market_value=float(p.market_value), unrealized_pl=float(p.unrealized_pl)))
    return rows

def place_order(symbol: str, qty: int, side: str, type_: str="market", limit_price: float|None=None):
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    tc = _trading_client()
    if type_ == "market":
        req = MarketOrderRequest(symbol=symbol, qty=qty, side=OrderSide(side), time_in_force=TimeInForce.DAY)
    else:
        if limit_price is None:
            raise ProviderError("limit_price required for limit order")
        req = LimitOrderRequest(symbol=symbol, qty=qty, side=OrderSide(side), limit_price=limit_price, time_in_force=TimeInForce.DAY)
    order = tc.submit_order(req)
    return {"id": order.id, "status": order.status, "symbol": order.symbol}

def cancel_all():
    tc = _trading_client()
    tc.cancel_orders()
    return True
