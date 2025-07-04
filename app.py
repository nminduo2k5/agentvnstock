# app.py
"""
Main Entry Point cho AI Trading Team Vietnam
Khởi chạy Streamlit application
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import main dashboard
try:
    from ui.main_dashboard import main as dashboard_main
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.error("🔧 Please ensure all required files are in the correct directory structure")
    st.stop()

# Initialize portfolio_data in session state if not already present
if "portfolio_data" not in st.session_state:
    st.session_state["portfolio_data"] = None  # or use an empty dict/list as appropriate

def main():
    """Main application entry point"""
    try:
        # Check for required environment
        check_requirements()
        
        # Run main dashboard
        dashboard_main()
        
    except Exception as e:
        render_error_page(e)

def check_requirements():
    """Check if all requirements are met"""
    
    required_modules = [
        'google.generativeai',
        'streamlit', 
        'pandas',
        'plotly',
        'requests',
        'asyncio'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        st.error("❌ Missing required dependencies!")
        st.markdown("### 📦 Please install missing packages:")
        
        for module in missing_modules:
            st.code(f"pip install {module}")
        
        st.markdown("### Or install all at once:")
        st.code("pip install -r requirements.txt")
        
        st.stop()

def render_error_page(error: Exception):
    """Render error page with debugging info"""
    
    st.title("🚨 Application Error")
    
    st.error(f"**Error Type:** {type(error).__name__}")
    st.error(f"**Error Message:** {str(error)}")
    
    # Debugging information
    with st.expander("🔧 Debugging Information"):
        st.code(f"""
Current Directory: {os.getcwd()}
Python Path: {sys.path[:3]}...
Streamlit Version: {st.__version__}
Error Details: {error}
        """)
    
    # Troubleshooting guide
    st.markdown("""
    ### 🛠️ Troubleshooting Guide
    
    1. **Check Dependencies**: Ensure all packages are installed
    ```bash
    pip install -r requirements.txt
    ```
    
    2. **Check File Structure**: Ensure all files are in correct locations
    ```
    ai-trading-team-vietnam/
    ├── app.py
    ├── requirements.txt
    └── src/
        ├── agents/
        ├── data/
        ├── ui/
        └── utils/
    ```
    
    3. **Check API Key**: Ensure Google GenAI API key is valid
    
    4. **Restart Application**: Try restarting Streamlit
    ```bash
    streamlit run app.py
    ```
    """)
    
    # Contact info
    st.info("""
    🆘 **Need Help?**  
    
    - Check the README.md file for setup instructions
    - Ensure Python 3.8+ is installed
    - Verify all dependencies are correctly installed
    - Check internet connection for API calls
    """)

if __name__ == "__main__":
    main()