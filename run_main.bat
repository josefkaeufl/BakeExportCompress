@echo off
setlocal

echo Überprüfe, ob pip verfügbar ist...
pip --version >nul 2>&1

if errorlevel 1 (
    echo pip ist nicht installiert. Bitte installieren Sie pip, bevor Sie fortfahren.
    exit /b 1
)

echo pip ist installiert.
echo Überprüfe und installiere fehlende Bibliotheken...

REM Überprüft jedes Paket in der requirements.txt und installiert es, falls nicht vorhanden
for /f %%i in (requirements.txt) do (
    echo Überprüfe %%i...
    pip show %%i >nul 2>&1
    if errorlevel 1 (
        echo Installiere %%i...
        pip install %%i
    )
)

echo Starte das Python-Skript...
python main.py

endlocal

