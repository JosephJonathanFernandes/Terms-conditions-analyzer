#!/usr/bin/env bash
# ClauseClear installer (macOS / Linux)
set -euo pipefail

cd "$(dirname "$0")"

echo "========================================"
echo " ClauseClear - Setup"
echo "========================================"

# Backend
echo "[1/4] Setting up Python backend..."
if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
fi
source backend/.venv/bin/activate
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from .env.example"
fi
cd ..

# Frontend
echo "[2/4] Setting up Node.js frontend..."
cd frontend
if [ ! -d node_modules ]; then
  npm install
fi
cd ..

echo
echo "[3/4] Setup complete."
echo
echo "[4/4] To run:"
echo "  Backend:  cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
echo "  Frontend: cd frontend && npm run dev"
echo "Then open http://localhost:5173"
echo "========================================"
