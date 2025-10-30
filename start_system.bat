@echo off
echo ========================================
echo   Assistive HAR System - Startup
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Dashboard Server...
start "HAR Dashboard" cmd /k "venv\Scripts\python.exe dashboard.py"

timeout /t 3 /nobreak > nul

echo Starting HAR Monitoring System...
echo.
echo INSTRUCTIONS:
echo - The dashboard is running at http://127.0.0.1:5000
echo - Press ESC in the camera window to exit
echo - Check the dashboard for real-time monitoring
echo.
echo ========================================
echo.

venv\Scripts\python.exe gesture_holistic.py

echo.
echo System shutdown complete.
pause
