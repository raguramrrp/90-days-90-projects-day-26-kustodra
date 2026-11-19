@echo off
setlocal

cd /d "%~dp0"

echo ======================================================================
echo    TRACEVAULT - Running Automated Test Suite
echo ======================================================================

if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found.
    echo Please run setup.bat first.
    exit /b 1
)

echo Executing automated pytest test suite across crypto, metadata, custody, and reports...
echo.

.\.venv\Scripts\python.exe -m pytest tests -v --tb=short

if %errorlevel% neq 0 (
    echo.
    echo [FAIL] One or more automated tests failed.
    exit /b %errorlevel%
)

echo.
echo [PASS] All 21 TRACEVAULT automated test cases passed successfully!
exit /b 0
