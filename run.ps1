Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting FitMind AI - Health & Fitness Coach" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

if (Test-Path "C:\Users\Dhanush\anaconda3\python.exe") {
    & "C:\Users\Dhanush\anaconda3\python.exe" app.py
} else {
    python app.py
}
