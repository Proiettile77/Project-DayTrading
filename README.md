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

## 🔐 Credenziali & Deploy

L'app supporta più provider con un **wizard di primo login** e un pannello "Impostazioni" per ruotare/migrare le chiavi.

Provider attivi di default:

- **Alpaca Paper** – trading demo su azioni USA
- **OANDA Practice** – forex demo
- **Binance Spot Testnet** – crypto demo

### Ordine di precedenza

1. Variabili d'ambiente
2. `st.secrets` (`.streamlit/secrets.toml`)
3. Keyring del sistema operativo
4. File `.env`

I salvataggi sono **non distruttivi**: quando si scrive su `.env` viene creato un backup `.env.bak` e le chiavi esistenti vengono mantenute.

### Backend di storage

| Backend        | Vantaggi                              | Svantaggi |
|---------------|---------------------------------------|-----------|
| Keyring       | Sicuro, consigliato per uso locale    | Dipende dal sistema operativo |
| `st.secrets`  | Comodo in deploy (Streamlit Cloud)    | File non cifrato su disco |
| `.env`        | Semplice per sviluppo locale          | Non cifrato, va escluso da Git |

`.env` e `.streamlit/secrets.toml` sono già ignorati da Git; usa `.env.example` come riferimento.

### Setup rapido

1. Avvia l'app e segui il wizard: scegli provider → inserisci API Key/Secret/Base URL → scegli backend → **Salva & Test**.
2. Nella tab "Impostazioni" puoi verificare lo stato (icone ✅/⚠️/❌), mostrare i secret mascherati, ruotare o cancellare le chiavi.
3. Per migrare le chiavi tra backend, usa il wizard scegliendo una destinazione diversa; lo `.env` originale viene mantenuto con backup.

Esempio `.env` generato:

```bash
ENABLE_ALPACA=true
APCA_API_KEY_ID=pk_xxxxxxxxxxxxxxxx
APCA_API_SECRET_KEY=sk_xxxxxxxxxxxxxxxx
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

### Dipendenze

Installazione librerie aggiuntive:

```bash
pip install python-dotenv keyring
```

`keyring` utilizza backend diversi a seconda dell'OS:

- **macOS**: Keychain integrato
- **Windows**: Credential Manager
- **Linux**: SecretService/Keyring (potrebbero servire pacchetti `gnome-keyring`/`libsecret`)

# 📌 Come ottenere le API Key Alpaca:

- Registrati su Alpaca.
- Accedi alla dashboard Paper Trading.
- Sezione API Keys → Genera e copia API Key ID (pk_...) e Secret Key (sk_...).

---

### Avvio rapido

- **macOS / Linux**:

```bash
cd cartellaProggetto
chmod +x ./run.sh
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
