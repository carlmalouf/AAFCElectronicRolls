@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo.
echo Starting Streamlit application...
streamlit run app.py
