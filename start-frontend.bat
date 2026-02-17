@echo off
echo Starting Todo App Frontend...
echo.

cd frontend

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
call npm install

echo.
echo Starting Vite dev server on http://localhost:3000
echo.

call npm run dev
