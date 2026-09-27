@echo off
title MindPulse - Automated Test Suite
cls
echo Running MindPulse Automated Unit Tests...
echo.
python -m unittest discover tests
echo.
echo Press any key to close this window...
pause >nul
