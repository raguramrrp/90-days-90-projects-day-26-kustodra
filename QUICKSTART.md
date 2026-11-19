# TRACEVAULT - Quick Start Guide

Get up and running in under 2 minutes on Windows.

## Automated Setup (Recommended)

1. Open a Command Prompt or PowerShell in this project folder.
2. Run the setup script:
   ```cmd
   setup.bat
   ```
   This will create `.venv`, install dependencies, initialize the database, and seed realistic demo files.

3. Launch the workstation:
   ```cmd
   run.bat
   ```
4. Open your browser at `http://localhost:8501`.

## Manual Setup

```cmd
:: 1. Create and activate virtual environment
python -m venv .venv
call .venv\Scripts\activate.bat

:: 2. Install requirements
pip install -r requirements.txt

:: 3. Seed demo database
python scripts\seed_demo_data.py

:: 4. Run tests
pytest tests -v

:: 5. Start workstation
streamlit run app.py
```
