@echo off
REM ClauseClear Windows installer
REM Creates venvs, installs dependencies, copies .env.example, starts servers

setlocal enabledelayedexpansion

echo ========================================
echo  ClauseClear - Setup (Windows)
echo ========================================

cd /d "%~dp0"

REM --- Backend ---
echo.
echo [1/4] Setting up Python backend...
if not exist "backend\.venv" (
    python -m venv backend\.venv
)
call backend\.venv\Scripts\activate.bat
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist ".env" (
    copy .env.example .env
    echo .env created from .env.example
)
cd ..

REM --- Frontend ---
echo.
echo [2/4] Setting up Node.js frontend...
cd frontend
if not exist "node_modules" (
    npm install
)
cd ..

REM --- Done ---
echo.
echo [3/4] Setup complete.
echo.
echo [4/4] To run:
echo   Backend:  cd backend && .venv\Scripts\activate && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo   Frontend: cd frontend && npm run dev
echo.
echo Then open http://localhost:5173
echo ========================================

endlocal
