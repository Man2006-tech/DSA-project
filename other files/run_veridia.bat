@echo off
title Veridia Search Engine
echo ===================================================
echo      Starting Veridia Search Engine...
echo ===================================================
echo.

cd Veridia_Core
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Could not find Veridia_Core directory!
    echo Please make sure you are running this from the project root.
    pause
    exit /b
)

echo Launching Production Server...
echo Open http://127.0.0.1:5000 in your browser once it says "Serving"
echo.

python run_production.py

pause
