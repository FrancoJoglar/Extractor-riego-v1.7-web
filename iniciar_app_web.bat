@echo off
chcp 65001 >nul
echo =========================================
echo   RIEGO EXTRACTOR v1.7 - INICIADOR
echo =========================================
echo.

echo [1/3] Verificando puertos ocupados...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
    echo       Matando proceso %%a en puerto 8501...
    taskkill //F //PID %%a >nul 2>&1
)
echo.

echo [2/3] Iniciando aplicacion Streamlit...
start "Streamlit" cmd //c "cd /d "%~dp0streamlit_app" && python -m streamlit run app.py"
echo       Esperando que inicie (5 segundos)...
timeout /t 5 /nobreak >nul
echo.

echo [3/3] Abriendo navegador...
start http://localhost:8501
echo.

echo =========================================
echo   APLICACION INICIADA
echo   http://localhost:8501
echo =========================================
echo.
echo Presiona cualquier tecla para salir...
pause >nul
