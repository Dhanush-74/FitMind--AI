@echo off
cd /d "%~dp0"

echo ===================================================
echo   Pushing FitMind AI to Dhanush-74/FitMind--AI
echo ===================================================
echo.

git remote remove origin 2>nul
git remote add origin https://github.com/Dhanush-74/FitMind--AI.git
git branch -M main
git push -u origin main

echo.
echo ===================================================
echo   Done! Check your Render dashboard now.
echo ===================================================
pause
