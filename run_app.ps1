# Activate virtual environment and run Streamlit app
.\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Cyan
streamlit run app.py
