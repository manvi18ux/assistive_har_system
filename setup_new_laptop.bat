@echo off
echo ========================================
echo   Assistive HAR System - Setup Script
echo ========================================
echo.

echo Checking Python 3.11...
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11 not found!
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    pause
    exit /b 1
)

echo Python 3.11 found!
echo.

echo Creating virtual environment...
py -3.11 -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To run the project:
echo   1. Double-click start_system.bat
echo   OR
echo   2. Run: venv\Scripts\python.exe gesture_holistic.py
echo.
echo Dashboard will be available at:
echo   http://127.0.0.1:5000
echo.
pause
