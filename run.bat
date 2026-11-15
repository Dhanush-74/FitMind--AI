@echo off
title FitMind AI - Health & Fitness Coach
cd /d "%~dp0"

echo ========================================================
echo   Starting FitMind AI - Health & Fitness Coach
echo ========================================================

if exist "C:\Users\Dhanush\anaconda3\python.exe" (
    "C:\Users\Dhanush\anaconda3\python.exe" app.py
) else (
    python app.py
)

pause
