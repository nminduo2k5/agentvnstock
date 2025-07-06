@echo off
echo ========================================
echo   DUONG AI TRADING SIUUUU - INSTALLER
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [4/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencies installed

echo.
echo [5/5] Setting up environment...
if not exist ".env" (
    echo # AI Trading System Configuration > .env
    echo GOOGLE_API_KEY=your_gemini_api_key_here >> .env
    echo GEMINI_MODEL=gemini-1.5-flash >> .env
    echo VNSTOCK_SOURCE=VCI >> .env
    echo DEBUG_MODE=False >> .env
    echo LOG_LEVEL=INFO >> .env
    echo ✅ .env file created
) else (
    echo .env file already exists, skipping...
)

echo.
echo ========================================
echo   INSTALLATION COMPLETED! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Google Gemini API key
echo 2. Run: streamlit run app.py
echo 3. Or run API: python api.py
echo.
echo Get API key at: https://aistudio.google.com/apikey
echo.
pause