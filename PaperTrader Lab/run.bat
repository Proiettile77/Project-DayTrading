@echo off
REM Avvia PaperTrader Lab dalla root del progetto

IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python -m streamlit run ui\app_streamlit.py
pause
