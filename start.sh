#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  Starting ORCA Marine Intelligence Platform (Phase 6)"
echo "============================================================"

echo "Starting Backend on http://127.0.0.1:8000 ..."
python backend/run.py &
BACKEND_PID=$!

sleep 2

echo "Starting Frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
