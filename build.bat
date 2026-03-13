@echo off
REM ============================================
REM Script para compilar Riego Extractor v1.5
REM ============================================

echo.
echo ============================================
echo COMPILANDO RIEGO EXTRACTOR v1.5
echo ============================================
echo.

REM 1. Instalar dependencias si no están
echo [1/3] Verificando dependencias...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo    - Instalando PyInstaller...
    pip install pyinstaller
)

REM 2. Compilar con PyInstaller
echo [2/3] Compilando con PyInstaller...
python -m PyInstaller build_spec.spec --clean

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo la compilacion con PyInstaller
    pause
    exit /b 1
)

REM 3. Crear instalador con Inno Setup
echo [3/3] Generando instalador...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" installer.iss
) else (
    echo    - Inno Setup no encontrado. Solo se creo el .exe
    echo    - Descarga Inno Setup desde https://jrsoftware.org/isinfo.php
    echo    - Luego ejecuta: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
)

echo.
echo ============================================
echo COMPILACION COMPLETADA
echo ============================================
echo.
echo Archivos generados:
if exist "dist\Riego_Extractor_v1.5.exe" echo   - dist\Riego_Extractor_v1.5.exe
if exist "installer\RiegoExtractor_v1.5_Setup.exe" echo   - installer\RiegoExtractor_v1.5_Setup.exe
echo.

pause
