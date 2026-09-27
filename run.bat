@echo off
title "MindPulse - Student Mental Health and Cognitive Wellness System"
cls

:: Check if Python is installed and accessible
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python from https://www.python.org or ensure it is added to your PATH.
    echo.
    pause
    exit /b 1
)

:: Run the application
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [INFO] Application exited with code %errorlevel%.
)

echo.
echo Press any key to close this window...
pause >nul
