#!/bin/bash

echo "========================================"
echo "  DUONG AI TRADING SIUUUU - INSTALLER"
echo "========================================"
echo

echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi
echo "✅ Python found"

echo
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

echo
echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

echo
echo "[5/5] Setting up environment..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# AI Trading System Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
VNSTOCK_SOURCE=VCI
DEBUG_MODE=False
LOG_LEVEL=INFO
EOF
    echo "✅ .env file created"
else
    echo ".env file already exists, skipping..."
fi

echo
echo "========================================"
echo "  INSTALLATION COMPLETED! 🎉"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env file and add your Google Gemini API key"
echo "2. Run: streamlit run app.py"
echo "3. Or run API: python api.py"
echo
echo "Get API key at: https://aistudio.google.com/apikey"
echo