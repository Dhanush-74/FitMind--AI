@echo off
title GitHub 1-Click Login and Push
cd /d "%~dp0"

echo ========================================================
echo   Logging into GitHub (1-Click in your Browser)
echo ========================================================
echo.

"C:\Program Files\GitHub CLI\gh.exe" auth login -h github.com -p https -w

echo.
echo ========================================================
echo   Configuring Git and Pushing to Dhanush-74/FitMind--AI...
echo ========================================================
"C:\Program Files\GitHub CLI\gh.exe" auth setup-git

git branch -M main
git push -u origin main

echo.
echo ========================================================
echo   Successfully pushed to GitHub!
echo   Render will now build your live site automatically!
echo ========================================================
pause
