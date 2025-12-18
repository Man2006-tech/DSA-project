@echo off
echo ========================================================
echo   VERIDIA SEARCH - DATA CONVERTER (TURBO MODE)
echo ========================================================
echo.
echo Starting conversion process...
echo This window will show:
echo  - Files Converted
echo  - Current Speed (files/sec)
echo.
echo Press Ctrl+C to stop at any time.
echo.

python Backend/convert_fast.py

echo.
echo ========================================================
echo   CONVERSION FINISHED
echo ========================================================
pause
