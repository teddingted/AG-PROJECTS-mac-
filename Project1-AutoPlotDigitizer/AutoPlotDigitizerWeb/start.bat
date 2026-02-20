@echo off
REM AutoPlotDigitizer Web Launcher for Windows

cd /d "%~dp0"

echo 🚀 Starting AutoPlotDigitizer Web...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    echo ✅ Setup complete!
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Run the app
python app.py

pause
