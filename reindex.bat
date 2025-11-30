@echo off
echo --- Veridia Search Engine: Updating Index ---
echo.
echo 1. Building Lexicon and Forward Index...
python VeridiaCore/build_index.py
echo.
echo 2. Building Inverted Index...
python VeridiaCore/inverted_index.py
echo.
echo --- Update Complete! ---
echo You can now run the search engine.
pause
