@echo off
echo ========================================
echo Starting Todo App (Local Development)
echo ========================================
echo.
echo This will start both backend and frontend in separate windows.
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo.
echo Press any key to continue...
pause > nul

echo.
echo Starting Backend...
start "Todo Backend" cmd /k "start-backend.bat"

timeout /t 3 /nobreak > nul

echo Starting Frontend...
start "Todo Frontend" cmd /k "start-frontend.bat"

echo.
echo Both services are starting in separate windows.
echo Close this window or press any key to exit.
pause > nul
