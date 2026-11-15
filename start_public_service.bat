@echo off
title FitMind AI - Public Cloudflare Web Service
cd /d "%~dp0"

echo ========================================================
echo   Launching FitMind AI Web Service & Public HTTPS Tunnel
echo ========================================================

start "" /B "C:\Users\Dhanush\anaconda3\python.exe" app.py
timeout /t 3 /nobreak >nul

echo Starting Cloudflare Tunnel...
"cloudflared.exe" tunnel --url http://127.0.0.1:8000
