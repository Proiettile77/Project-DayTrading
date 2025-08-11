# 📈 PaperTrader Lab – Simulatore Day Trading

> **ATTENZIONE:** Solo simulazione/paper trading.  
> Questa applicazione **non** costituisce consulenza finanziaria e **non** esegue ordini reali.  
> Usare solo con ambienti demo/test e nel rispetto dei ToS dei provider.

---

## 📦 Funzionalità

- **Backtest** con motore [Backtrader](https://www.backtrader.com/) su dati storici.
- **Strategie incluse**:
  - EMA crossover + ATR stop/take profit.
- **Paper Trading** in tempo reale con [Alpaca Paper Trading API](https://alpaca.markets/).
- **UI interattiva** con [Streamlit](https://streamlit.io/) e controlli completi per:
  - Parametri di mercato e dati.
  - Gestione del rischio e costi.
  - Parametri strategia.
- **Metriche**: CAGR, Sharpe/Sortino, Max Drawdown, Calmar, ecc.
- **Caching** dei dati per velocizzare le prove.
- Semplice modulo di machine learning per prevedere la direzione del prezzo.

---

## 🛠 Prerequisiti

- **Python 3.11+**
- Account demo Paper Trading su [Alpaca](https://alpaca.markets/) (per dati e ordini demo).
- (Opzionale) API Key gratuita di [Alpha Vantage](https://www.alphavantage.co/) per dati storici.

---

## 🔑 Configurazione

>Crea un file .env nella root del progetto con le tue API key:

```bash
# --- Feature flags ---
DEFAULT_ENGINE=backtrader
DEFAULT_DATA_PROVIDER=alpaca
ENABLE_ALPACA=true
ENABLE_OANDA=false
ENABLE_BINANCE=false

# --- Alpaca (Paper) ---
ALPACA_API_KEY=pk_xxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=sk_xxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets/v2
ALPACA_DATA_BASE_URL=https://data.alpaca.markets
ALPACA_DATA_FEED=iex   # iex = gratis, sip = a pagamento

# --- Alpha Vantage (opzionale) ---
ALPHAVANTAGE_API_KEY=AV_XXXXXXXXXXXX
```

# 📌 Come ottenere le API Key Alpaca:

- Registrati su Alpaca.
- Accedi alla dashboard Paper Trading.
- Sezione API Keys → Genera e copia API Key ID (pk_...) e Secret Key (sk_...).

---

### Avvio rapido

- **macOS / Linux**:

```bash
cd cartellaProggetto
./run.sh
```

- **Windows**:

```bash
run.bat
```

---

## 💡 Uso rapido

1. Sidebar – Mercato & Dati
    Scegli data source (alpaca o alphavantage).
    Seleziona strumenti (es. AAPL, TSLA), timeframe e intervallo date.
    (Opzionale) Filtra per orario di sessione e fuso orario.
2. Sidebar – Rischio & Costi
    Imposta rischio per trade, commissioni, slippage, leverage.
3. Sidebar – Strategia
    Parametri EMA, ATR e Stop/TP.
4. Backtest
    Premi Carica dati & backtest → guarda metriche e grafici.
5. Paper Trading
    Connetti a Alpaca Paper → invia ordini market o limit → visualizza posizioni.

---

## 📊 Metriche principali

- CAGR: rendimento annuo composto.
- Sharpe: rendimento aggiustato per volatilità.
- Sortino: come Sharpe, ma considera solo volatilità negativa.
- Max Drawdown: perdita massima dal picco.
- Calmar: CAGR / Max Drawdown.

---

## ⚠️ Limiti

- Solo simulazione → i risultati non riflettono necessariamente performance reali.
- Latenza e slippage possono differire dal live.
- Alpha Vantage ha limite di 25 richieste/giorno (usa il caching).
- Evitare overfitting nei parametri strategia.
