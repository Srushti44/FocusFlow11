$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot "backend\venv\Scripts\python.exe"
$pythonCommand = if (Test-Path $venvPython) {
	"& '$venvPython' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
} else {
	"python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
}
$encodedPythonCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($pythonCommand))

# Launch Backend
Write-Host "[1/2] Launching Python FastAPI Backend..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList "-NoExit", "-EncodedCommand", $encodedPythonCommand

# Launch Frontend
Write-Host "[2/2] Launching React Vite Frontend..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host ""
Write-Host "FocusFlow is now running!" -ForegroundColor Cyan
Write-Host " -> Web App:         http://localhost:5173" -ForegroundColor White
Write-Host " -> MLOps Dashboard: http://localhost:5173/?view=mlops" -ForegroundColor White
Write-Host " -> Backend API:     http://localhost:8000/docs" -ForegroundColor White
Write-Host " -> Chrome Ext Dir:  \extension (Load unpacked at chrome://extensions)" -ForegroundColor White
