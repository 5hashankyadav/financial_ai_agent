#!/bin/bash
echo "=================================================="
echo "STARTING FINANCIAL AI AGENT SERVER"
echo "=================================================="
echo "Server running at http://localhost:8000"
echo "Press Ctrl+C to stop the server."
echo "=================================================="

python3 -m uvicorn app.api:app --host 0.0.0.0 --port 8000
