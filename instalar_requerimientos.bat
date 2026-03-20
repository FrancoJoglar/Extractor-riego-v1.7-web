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

echo [3/4] Instalando paquetes uno por uno...
echo.

set PAQUETE_FALLIDO=

echo       Instalando streamlit...
pip install streamlit
if errorlevel 1 (
    echo       ERROR: Fallo streamlit
    set PAQUETE_FALLIDO=streamlit
    goto :verificar
)
echo       streamlit OK

echo       Instalando pandas...
pip install pandas
if errorlevel 1 (
    echo       ERROR: Fallo pandas
    set PAQUETE_FALLIDO=pandas
    goto :verificar
)
echo       pandas OK

echo       Instalando openpyxl...
pip install openpyxl
if errorlevel 1 (
    echo       ERROR: Fallo openpyxl
    set PAQUETE_FALLIDO=openpyxl
    goto :verificar
)
echo       openpyxl OK

echo       Instalando supabase...
pip install supabase
if errorlevel 1 (
    echo       ERROR: Fallo supabase
    set PAQUETE_FALLIDO=supabase
    goto :verificar
)
echo       supabase OK

echo       Instalando streamlit-extras...
pip install streamlit-extras
if errorlevel 1 (
    echo       ERROR: Fallo streamlit-extras
    set PAQUETE_FALLIDO=streamlit-extras
    goto :verificar
)
echo       streamlit-extras OK

goto :fin

:verificar
echo.
echo =========================================
echo   ERROR EN INSTALACION
echo =========================================
echo.
echo Paquete que fallo: %PAQUETE_FALLIDO%
echo.
echo Soluciones posibles:
echo 1. Usa Python 3.11 o 3.12 en vez de 3.14
echo 2. Verifica tu conexion a internet
echo 3. Intenta: pip install %PAQUETE_FALLIDO% --only-binary :all:
echo.
pause
exit /b 1

:fin
echo.
echo [4/4] Verificando instalacion completa...
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
