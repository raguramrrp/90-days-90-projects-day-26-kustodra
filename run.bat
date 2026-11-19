@echo off
setlocal

echo ======================================================================
echo    Starting TRACEVAULT - Digital Evidence Workstation
echo ======================================================================

if not exist .venv\Scripts\streamlit.exe (
    echo [ERROR] Virtual environment or Streamlit not detected.
    echo Please execute setup.bat first to configure dependencies.
    echo.
    pause
    exit /b 1
)

echo Activating environment and launching workstation interface...
echo Local URL: http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the workstation.
echo.

.\.venv\Scripts\streamlit.exe run app.py --server.port=8501 --server.headless=false

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] TRACEVAULT exited unexpectedly with code %errorlevel%.
    pause
)
