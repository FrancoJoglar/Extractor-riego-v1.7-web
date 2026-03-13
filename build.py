# Riego Extractor v1.5 - Build Script
# Genera .exe usando PyInstaller
# Uso: python build.py

import os
import shutil
import subprocess

# Cambiar al directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Limpiar anteriores builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('Riego Extractor v1.5.spec'):
    os.remove('Riego Extractor v1.5.spec')

print("Generando .exe con PyInstaller...")

# Ejecutar PyInstaller desde el directorio correcto
result = subprocess.run([
    'pyinstaller',
    'gui_app.py',
    '--name=Riego Extractor v1.5',
    '--onefile',
    '--windowed',
    '--add-data=requirements.txt;.',
    '--noconfirm',
    '--clean'
], cwd=script_dir)

if result.returncode == 0:
    print(f"\n✓ Ejecutable generado en: {script_dir}\\dist\\Riego Extractor v1.5.exe")
else:
    print(f"\n✗ Error al generar ejecutable")
