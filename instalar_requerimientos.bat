@echo off
chcp 65001 >nul
echo =========================================
echo   RIEGO EXTRACTOR v1.7 - INSTALADOR
echo =========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Descargalo de: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       %PYTHON_VERSION% OK
echo.

echo [2/4] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no esta disponible.
    pause
    exit /b 1
)
echo       pip OK
echo.

echo [3/4] Instalando requerimientos...
echo.

echo       Verificando version de pip...
python -m pip install --version

echo.
echo       - Instalando paquetes (puede tardar varios minutos en Python 3.14)...
echo       - Presiona Ctrl+C si tarda mas de 10 minutos
echo.

pip install streamlit pandas openpyxl supabase streamlit-extras --verbose
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de paquetes
    pause
    exit /b 1
)
echo.
echo [4/4] Verificando instalacion...
echo.

pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo ERROR: streamlit no se instalo correctamente
    pause
    exit /b 1
) else (
    echo       streamlit OK
)

pip show pandas >nul 2>&1
if errorlevel 1 (
    echo ERROR: pandas no se instalo correctamente
    pause
    exit /b 1
) else (
    echo       pandas OK
)

pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo ERROR: openpyxl no se instalo correctamente
    pause
    exit /b 1
) else (
    echo       openpyxl OK
)

pip show supabase >nul 2>&1
if errorlevel 1 (
    echo ERROR: supabase no se instalo correctamente
    pause
    exit /b 1
) else (
    echo       supabase OK
)

echo.
echo =========================================
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo =========================================
echo.
pause
