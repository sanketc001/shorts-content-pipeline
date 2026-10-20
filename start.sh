#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Shutting down..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup INT TERM

echo "Starting Content Studio..."
echo ""

# Start backend
echo "[1/2] Starting backend on http://localhost:8000"
cd "$DIR/backend"
pip install -r requirements.txt -q 2>/dev/null
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Starting frontend on http://localhost:5173"
cd "$DIR/frontend"
npm install --silent 2>/dev/null
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Content Studio is running:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."

wait
