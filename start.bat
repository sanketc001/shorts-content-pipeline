@echo off
title Content Studio

echo Starting Content Studio...
echo.

:: Start backend
echo [1/2] Starting backend on http://localhost:8000
cd /d "%~dp0backend"
start "Content Studio - Backend" cmd /k "pip install -r requirements.txt >nul 2>&1 && uvicorn main:app --reload --port 8000"

:: Start frontend
echo [2/2] Starting frontend on http://localhost:5173
cd /d "%~dp0frontend"
start "Content Studio - Frontend" cmd /k "npm install >nul 2>&1 && npm run dev"

echo.
echo Content Studio is starting...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
timeout /t 5 /nobreak >nul
start http://localhost:5173
