# --- add project root to sys.path ---
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ------------------------------------


import streamlit as st
import pandas as pd
import plotly.express as px
from utils.config import (
    SETTINGS,
    load_credentials,
    save_credentials,
    test_alpaca_credentials,
    current_storage_backend,
    reload_settings,
    clear_credentials,
)
from utils.logging_json import get_logger
from data.loader import load_ohlcv
from backtest.engine import run_backtest
from paper.router import connect_info
from paper import alpaca

log = get_logger("ui")

st.set_page_config(page_title="PaperTrader Lab — (Simulazione, non consulenza)", layout="wide")

# Bootstrap credenziali
creds_boot = load_credentials()
if not creds_boot.get("key"):
    st.session_state.setdefault("show_wizard", True)
else:
    st.session_state.setdefault("show_wizard", False)

# Disclaimer banner
st.info("**Solo simulazione / paper trading. Questa applicazione non costituisce consulenza finanziaria.** "
        "Usa esclusivamente ambienti demo/paper e rispetta i ToS dei provider.", icon="⚠️")

# ---- Sidebar Controls ----
with st.sidebar:
    st.header("Mercato & Dati")
    provider = st.selectbox("Data Source", ["alpaca","alphavantage"], index=["alpaca","alphavantage"].index(SETTINGS.default_data_provider))
    symbols = st.multiselect("Strumenti", ["AAPL","TSLA","MSFT","NVDA","AMZN"], default=["AAPL","TSLA"])
    timeframe = st.selectbox("Timeframe", ["1m","5m","15m","1h","D"], index=2)
    start_date = st.date_input("Start", pd.to_datetime("2024-01-01"))
    end_date = st.date_input("End", pd.Timestamp.today())
    tz = st.text_input("Fuso orario", "America/New_York")
    adjusted = st.checkbox("Adjusted", True)
    session_filter = st.checkbox("Filtra orari di sessione", True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        session_start = st.text_input("Session start", "09:30")
    with col_s2:
        session_end = st.text_input("Session end", "16:00")

    st.divider()
    st.header("Rischio & Costi")
    risk_per_trade = st.slider("Rischio per trade (% equity)", 0.1, 5.0, 1.0, 0.1) / 100.0
    max_portfolio_risk = st.slider("Rischio portafoglio max (%)", 1.0, 50.0, 20.0, 1.0)
    leverage = st.slider("Leverage (x)", 1.0, 5.0, 1.0, 0.5)
    commission_bps = st.slider("Commissioni (bps sul valore)", 0, 50, 5, 1)
    slippage_bps = st.slider("Slippage simulato (bps)", 0, 50, 5, 1)

    st.divider()
    st.header("Strategia")
    strategy_name = st.selectbox("Strategia", ["EMA crossover + ATR stop", "Breakout + filtro vol (soon)"], index=0)
    ema_fast = st.number_input("ema_fast", 5, 200, 12)
    ema_slow = st.number_input("ema_slow", 10, 400, 26)
    atr_window = st.number_input("ATR window", 5, 100, 14)
    stop_mode = st.selectbox("Stop/TP mode", ["atr","percent"], index=0)
    atr_mult_sl = st.number_input("ATR SL x", 0.5, 10.0, 2.0, 0.1)
    atr_mult_tp = st.number_input("ATR TP x", 0.5, 10.0, 3.0, 0.1)
    sl_pct = st.number_input("SL % (se percent)", 0.1, 50.0, 1.0, 0.1)/100.0
    tp_pct = st.number_input("TP % (se percent)", 0.1, 50.0, 2.0, 0.1)/100.0
    time_in_market_max = st.number_input("Max bars in trade (0=illimitato)", 0, 10000, 0)

@st.cache_data(show_spinner=True)
def cached_load(symbols, provider, timeframe, start_date, end_date, tz, session_filter, session_start, session_end, adjusted):
    df = load_ohlcv(
        symbols=symbols, provider=provider, timeframe=timeframe,
        start_date=str(start_date), end_date=str(end_date), tz=tz,
        session_filter_on=session_filter, session_start=session_start, session_end=session_end,
        adjusted=adjusted
    )
    return df

tabs = st.tabs(["Backtest", "Paper", "ML", "Log/Report", "Impostazioni"])

with tabs[0]:
    st.subheader("Backtest — Motore: Backtrader")
    if st.button("Carica dati & backtest", type="primary"):
        try:
            df = cached_load(symbols, provider, timeframe, start_date, end_date, tz, session_filter, session_start, session_end, adjusted)
            st.success(f"Dati caricati: {df['symbol'].nunique()} simboli, {len(df)} barre.")
            st.dataframe(df.tail(10))
            # Run backtest
            strategy_params = dict(
                ema_fast=ema_fast, ema_slow=ema_slow, atr_period=atr_window,
                stop_mode=stop_mode, atr_mult_sl=atr_mult_sl, atr_mult_tp=atr_mult_tp,
                sl_pct=sl_pct, tp_pct=tp_pct, time_in_market_max=(time_in_market_max or None)
            )
            result = run_backtest(
                df=df,
                cash=100_000 * leverage,
                commission=commission_bps/1e4,
                slippage_bps=slippage_bps,
                sizer_kwargs=dict(risk_per_trade=risk_per_trade, min_size=1),
                strategy_params=strategy_params
            )
            st.session_state["bt_result"] = result
        except Exception as e:
            st.error(f"Errore: {e}")

    if "bt_result" in st.session_state:
        res = st.session_state["bt_result"]
        m = res["metrics"]
        st.markdown("### Metriche")
        st.write(pd.DataFrame([m]).T.rename(columns={0:"value"}))
        st.markdown("### Equity Curve")
        eq = res["equity"]
        fig = px.line(eq, labels={"value":"Equity (rel.)","index":"Data"})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### Per-symbol summary")
        st.dataframe(pd.DataFrame(res["per_symbol"]))

with tabs[1]:
    st.subheader("Paper Trading — Alpaca (Paper)")
    if SETTINGS.enable_alpaca:
        if st.button("Connetti/refresh"):
            st.session_state["conn"] = connect_info()
        if "conn" in st.session_state:
            st.json(st.session_state["conn"])
        st.markdown("**Ordine rapido**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            psym = st.selectbox("Symbol", symbols or ["AAPL"])
        with c2:
            side = st.selectbox("Side", ["buy","sell"])
        with c3:
            qty = st.number_input("Qty", 1, 1_000, 1)
        with c4:
            otype = st.selectbox("Type", ["market","limit"])
        limit_price = None
        if otype == "limit":
            limit_price = st.number_input("Limit price", 0.0, 1_000_000.0, 100.0)
        if st.button("Invia ordine"):
            try:
                resp = alpaca.place_order(psym, int(qty), side, type_=otype, limit_price=limit_price)
                st.success(f"Ordine inviato: {resp}")
            except Exception as e:
                st.error(f"Errore ordine: {e}")
        if st.button("Cancella TUTTI gli ordini"):
            try:
                alpaca.cancel_all()
                st.success("Ordini cancellati.")
            except Exception as e:
                st.error(str(e))
        st.markdown("**Posizioni**")
        try:
            st.dataframe(pd.DataFrame(alpaca.positions()))
        except Exception as e:
            st.error(f"Errore posizioni: {e}")
    else:
        st.warning("Alpaca disabilitato. Abilita ENABLE_ALPACA=true nel .env")

with tabs[2]:
    st.subheader("ML (opzionale) — Triple-Barrier & Purged/CPCV (stub)")
    st.caption("Labeling con Triple-Barrier (PT/SL/holding), meta-labeling on/off; CV anti-leakage: Purged K-Fold / CPCV con embargo. Riferimenti: López de Prado, AFML.")
    st.markdown("- Triple-Barrier: etichettatura con barriera verticale e 2 orizzontali (SL/TP).")
    st.markdown("- Purged K-Fold & CPCV: split time-series senza leakage con **embargo**.")
    st.info("Implementazioni complete saranno aggiunte nei moduli ml/*. Riferimenti in README.")

with tabs[3]:
    st.subheader("Log / Report")
    st.write("Eventi principali (JSON)")
    st.code('{"ts":"...","level":"INFO","name":"ui","msg":"example"}', language="json")

with tabs[4]:
    st.subheader("Impostazioni")
    creds = load_credentials()
    backend = current_storage_backend()
    status = "missing"
    detail = ""
    if creds.get("key"):
        ok, err = test_alpaca_credentials(creds["key"], creds["secret"], creds["base_url"])
        if ok:
            status = "ok"
        else:
            status = "error"
            detail = err
    if status == "ok":
        st.success("Credenziali verificate", icon="✅")
    elif status == "error":
        st.error("Errore credenziali", icon="❌")
        if detail:
            st.caption(detail)
    else:
        st.warning("Credenziali mancanti", icon="⚠️")

    if st.session_state.get("show_wizard", False) or status != "ok":
        st.info(
            "Inserisci le tue credenziali Alpaca Paper. Le chiavi non saranno salvate nel repository Git.",
            icon="ℹ️",
        )
        api_key = st.text_input("API Key")
        secret_key = st.text_input("Secret", type="password")
        base_url = st.text_input(
            "Base URL",
            value=creds.get("base_url", "https://paper-api.alpaca.markets"),
        )
        labels = {"keyring": "Keychain (consigliato)", "secrets": "secrets.toml", "env_file": ".env"}
        target = st.selectbox("Metodo di archiviazione", list(labels.keys()), format_func=lambda x: labels[x])
        if st.button("Salva & Test", type="primary"):
            if not api_key or not secret_key:
                st.error("API Key e Secret obbligatorie")
            else:
                try:
                    save_credentials(target, api_key, secret_key, base_url)
                    ok, err = test_alpaca_credentials(api_key, secret_key, base_url)
                    if ok:
                        reload_settings()
                        st.session_state["show_wizard"] = False
                        st.success("Credenziali verificate e salvate")
                    else:
                        st.error(f"Verifica fallita: {err}")
                except Exception as e:
                    st.error(f"Salvataggio fallito: {e}. Prova un altro metodo.")
        st.caption("Le chiavi sono memorizzate localmente nel backend scelto.")
    else:
        show = st.checkbox("Mostra secret", value=False)
        st.text_input("API Key", creds.get("key"), disabled=True)
        st.text_input(
            "Secret",
            creds.get("secret") if show else "*" * len(creds.get("secret", "")),
            disabled=True,
        )
        st.write(f"Storage attuale: {backend or 'N/D'}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ruota chiavi"):
                st.session_state["show_wizard"] = True
        with col2:
            if st.button("Logout"):
                if backend:
                    clear_credentials(backend)
                reload_settings()
                st.session_state["show_wizard"] = True
                st.warning("Credenziali rimosse")
