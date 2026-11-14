@echo off
echo ==============================================
echo       FOCUSFLOW - STARTING FULL STACK
echo ==============================================
cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
if exist "backend\venv\Scripts\python.exe" (
	start "FocusFlow Backend" cmd /k ""%~dp0backend\venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
) else (
	start "FocusFlow Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
)

echo [2/2] Starting React Vite Frontend on http://localhost:5173 ...
start "FocusFlow Frontend" cmd /k "npm run dev"

echo ==============================================
echo FocusFlow running!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo Chrome Extension folder: focusflow\extension
echo ==============================================
