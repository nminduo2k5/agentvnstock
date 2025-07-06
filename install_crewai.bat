@echo off
echo ========================================
echo  Installing CrewAI Integration
echo ========================================

echo.
echo [1/3] Installing CrewAI dependencies...
pip install crewai[tools]>=0.117.0
pip install crewai-tools>=0.12.0

echo.
echo [2/3] Upgrading existing packages...
pip install --upgrade google-generativeai
pip install --upgrade vnstock
pip install --upgrade streamlit

echo.
echo [3/3] Testing installation...
python -c "import crewai; print('✅ CrewAI installed successfully')"
python -c "from crewai_tools import SerperDevTool, ScrapeWebsiteTool; print('✅ CrewAI tools available')"

echo.
echo ========================================
echo  CrewAI Integration Ready!
echo ========================================
echo.
echo Next steps:
echo 1. Get Gemini API key: https://aistudio.google.com/apikey
echo 2. Get Serper API key: https://serper.dev/api-key
echo 3. Run: streamlit run src/ui/dashboard.py
echo.
pause