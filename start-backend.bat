@echo off
echo Starting Todo App Backend...
echo.

cd backend

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8001
echo API docs will be available at http://localhost:8001/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
