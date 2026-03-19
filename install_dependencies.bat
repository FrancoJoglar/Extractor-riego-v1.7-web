@echo off
setlocal enabledelayedexpansion

echo ================================================
echo   RIEGO EXTRACTOR v1.7 - Instalador
echo ================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Ejecutando como administrador...
)

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

:: ============================================================================
:: 1. CHECK PYTHON
:: ============================================================================
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo.
    echo Por favor instala Python 3.10 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marca "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo     Python %PYTHON_VERSION% encontrado.

:: ============================================================================
:: 2. UPGRADE PIP
:: ============================================================================
echo.
echo [2/5] Actualizando pip...
python -m pip --quiet install --upgrade pip

:: ============================================================================
:: 3. INSTALL DEPENDENCIES
:: ============================================================================
echo.
echo [3/5] Instalando dependencias...

if exist "requirements.txt" (
    echo     Instalando desde requirements.txt...
    python -m pip --quiet install -r requirements.txt
    if %errorLevel% neq 0 (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
    echo     Dependencias instaladas.
) else (
    echo [WARNING] requirements.txt no encontrado.
)

:: Install Streamlit if not present
python -c "import streamlit" >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo     Instalando Streamlit...
    python -m pip --quiet install streamlit
)

:: ============================================================================
:: 4. CONFIGURAR SECRETS
:: ============================================================================
echo.
echo [4/5] Configurando secrets...

if not exist "streamlit_app\.streamlit\secrets.toml" (
    if exist "streamlit_app\.streamlit\secrets.toml.example" (
        copy "streamlit_app\.streamlit\secrets.toml.example" "streamlit_app\.streamlit\secrets.toml"
        echo     secrets.toml creado desde template.
        echo.
        echo [IMPORTANTE] Edita streamlit_app\.streamlit\secrets.toml
        echo y completa tus credenciales de Supabase.
    ) else (
        echo [WARNING] secrets.toml.example no encontrado.
    )
) else (
    echo     secrets.toml ya existe.
)

:: ============================================================================
:: 5. VERIFICACION
:: ============================================================================
echo.
echo [4/5] Verificando instalacion...

set "ALL_OK=true"

python -c "import pandas" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] pandas no instalado.
    set "ALL_OK=false"
)

python -c "import supabase" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] supabase no instalado.
    set "ALL_OK=false"
)

python -c "import openpyxl" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] openpyxl no instalado.
    set "ALL_OK=false"
)

python -c "import streamlit" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] streamlit no instalado.
    set "ALL_OK=false"
)

:: ============================================================================
:: FINAL
:: ============================================================================
echo.
echo ================================================
if "%ALL_OK%"=="true" (
    echo   INSTALACION COMPLETADA EXITOSAMENTE
    echo ================================================
    echo.
    echo Para ejecutar la aplicacion:
    echo   cd streamlit_app
    echo   streamlit run app.py
    echo.
    echo O usa el lanzador: iniciar_app.bat
    echo.
    echo NO OLVIDES configurar secrets.toml con tus
    echo credenciales de Supabase.
) else (
    echo   HUBO ERRORES EN LA INSTALACION
    echo ================================================
    echo.
    echo Revisa los mensajes de error arriba.
    echo.
    echo Si el problema persiste, intenta:
    echo   pip install --force-reinstall -r requirements.txt
)
echo.
pause
