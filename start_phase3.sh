#!/bin/bash
# Phase III Startup Script

echo "==================================="
echo "Phase III: AI Chatbot Startup"
echo "==================================="
echo ""

# Check if OpenAI API key is set
if grep -q "your-openai-api-key-here" backend/.env; then
    echo "⚠️  WARNING: OpenAI API key not configured!"
    echo "Please update backend/.env with your OpenAI API key"
    echo ""
fi

echo "Starting services..."
echo ""

# Start MCP Server
echo "1. Starting MCP Server (port 8002)..."
cd backend
python mcp_server.py &
MCP_PID=$!
cd ..

sleep 3

# Start Backend API
echo "2. Starting Backend API (port 8001)..."
cd backend
python -m uvicorn app.main:app --reload --port 8001 &
BACKEND_PID=$!
cd ..

sleep 3

# Start Frontend
echo "3. Starting Frontend (port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "==================================="
echo "✅ All services started!"
echo "==================================="
echo ""
echo "MCP Server: http://localhost:8002"
echo "Backend API: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $MCP_PID $BACKEND_PID $FRONTEND_PID; exit" INT
wait
