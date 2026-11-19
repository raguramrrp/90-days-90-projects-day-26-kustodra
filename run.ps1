# TRACEVAULT - PowerShell Launcher
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   Starting TRACEVAULT - Digital Evidence Workstation" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtual environment not found at $VenvPython" -ForegroundColor Red
    Write-Host "Please execute setup.bat or setup manually."
    exit 1
}

Write-Host "Activating environment and launching workstation interface..." -ForegroundColor Green
Write-Host "Local URL: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop.`n"

& $VenvPython -m streamlit run app.py --server.port=8501 --server.headless=false
