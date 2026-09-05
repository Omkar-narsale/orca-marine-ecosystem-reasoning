@echo off
echo ============================================================
echo   Starting ORCA Marine Intelligence Platform (Phase 6)
echo ============================================================
echo.
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "ORCA Backend" cmd /k "python backend/run.py"

echo Waiting 2 seconds for backend initialization...
timeout /t 2 /nobreak >nul

echo Starting Next.js Frontend on http://localhost:3000 ...
start "ORCA Frontend" cmd /k "npm run dev"

echo.
echo ORCA is running!
echo Frontend: http://localhost:3000
echo Backend Docs: http://127.0.0.1:8000/docs
echo Health Check: http://127.0.0.1:8000/health
echo.
pause
