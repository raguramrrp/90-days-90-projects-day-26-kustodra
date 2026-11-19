@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo ======================================================================
echo    TRACEVAULT - Digital Evidence Integrity & Custody Setup (Windows)
echo    Day 26 - 90 Days 90 Projects Challenge
echo ======================================================================
echo.

:: 1. Check for Python installation
echo [1/5] Checking Python installation...
set PYTHON_CMD=

py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.12
    goto PYTHON_FOUND
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto PYTHON_FOUND
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto PYTHON_FOUND
)

echo [ERROR] No compatible Python runtime found.
echo Please install Python 3.11 or 3.12 from https://www.python.org/
exit /b 1

:PYTHON_FOUND
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version

:: 2. Create virtual environment
echo.
echo [2/5] Configuring project virtual environment (.venv)...
if not exist .venv (
    echo Creating virtual environment at .venv...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists (.venv).
)

:: 3. Install dependencies
echo.
echo [3/5] Installing core dependencies (Streamlit, ReportLab, Pandas, Pillow, Pytest)...
.\.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Online pip install failed or was blocked by network restriction.
    echo Checking if core packages are already present in venv...
    .\.venv\Scripts\python.exe -c "import streamlit, reportlab, pandas, PIL; print('[OK] Core dependencies verified in environment.')" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Required dependencies are missing and could not be installed.
        exit /b 1
    )
)

:: 4. Environment configuration
echo.
echo [4/5] Checking environment configuration...
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env >nul
) else (
    echo Existing .env preserved.
)

:: 5. Initialize database and seed demo data
echo.
echo [5/5] Initializing SQLite schema and seeding forensic demo data...
.\.venv\Scripts\python scripts\seed_demo_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to seed database.
    exit /b 1
)

echo.
echo ======================================================================
echo    TRACEVAULT Setup Complete!
echo ======================================================================
echo To start the workstation, run:  run.bat
echo To execute automated tests, run: test.bat
echo.
exit /b 0
