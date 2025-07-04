#!/usr/bin/env python3
"""
Streamlit App Entry Point
AI Trading Team Vietnam - 6 Agents + Gemini Chatbot
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.dashboard import main

if __name__ == "__main__":
    main()