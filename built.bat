@echo off
echo ============================================================
echo    VERIDIA SEARCH ENGINE - BUILD ALL INDICES
echo ============================================================
echo.
echo This will build all indices for the search engine.
echo This may take several minutes...
echo.
pause

python build_all.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo You can now run: run.bat
    echo Or manually: python app.py
    echo.
) else (
    echo.
    echo ============================================================
    echo BUILD FAILED!
    echo ============================================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause