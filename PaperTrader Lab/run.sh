#!/bin/bash
# Avvia PaperTrader Lab dalla root del progetto

# Attiva virtualenv se esiste
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Avvio Streamlit
python -m streamlit run ui/app_streamlit.py
