@echo off
REM Phase III Quick Start Script for Windows

echo ========================================
echo Phase III: AI Chatbot Quick Start
echo ========================================
echo.

REM Check if OpenAI API key is configured
findstr /C:"your-openai-api-key-here" backend\.env >nul
if %errorlevel% equ 0 (
    echo [WARNING] OpenAI API key not configured!
    echo Please update backend\.env with your OpenAI API key
    echo Get one at: https://platform.openai.com/api-keys
    echo.
    pause
)

echo Starting services...
echo.

REM Start MCP Server
echo [1/3] Starting MCP Server on port 8002...
start "MCP Server" cmd /k "cd backend && python mcp_server.py"
timeout /t 3 /nobreak >nul

REM Start Backend API
echo [2/3] Starting Backend API on port 8001...
start "Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8001"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [3/3] Starting Frontend on port 3000...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo MCP Server:  http://localhost:8002
echo Backend API: http://localhost:8001
echo Frontend:    http://localhost:3000
echo.
echo Press any key to stop all services...
pause >nul

REM Kill all services
taskkill /FI "WindowTitle eq MCP Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Backend API*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend*" /F >nul 2>&1

echo Services stopped.
