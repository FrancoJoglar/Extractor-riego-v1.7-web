@echo off
cd /d "%~dp0"
echo ============================================
echo   RIEGO EXTRACTOR v1.7 - WEB
echo ============================================
echo.
pip install -r streamlit_app/requirements.txt 2>nul
streamlit run streamlit_app/app.py
pause
