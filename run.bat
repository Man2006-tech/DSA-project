@echo off
echo ============================================================
echo    VERIDIA SEARCH ENGINE - STARTING
echo ============================================================
echo.
echo Cleaning up previous instances...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting Flask web server...
echo Server will run at: http://127.0.0.1:5001
echo.
echo Opening Browser...
start "" "http://localhost:5001"
echo.
echo Press Ctrl+C to stop the server (or close this window)
echo.
echo ============================================================
echo.

python -O Backend/app.py

pause