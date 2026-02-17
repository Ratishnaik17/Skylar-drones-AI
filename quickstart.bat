@echo off
REM Quick start script for Windows users

echo.
echo ================================================
echo.  AI OPERATIONS BRAIN - QUICK START (Windows)
echo.
echo ================================================
echo.

REM Check Python version
python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo.Creating virtual environment...
    python -m venv venv
    echo.OK - Virtual environment created
) else (
    echo.OK - Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo.OK - Virtual environment activated
echo.

REM Install dependencies
echo.Installing dependencies...
pip install -r requirements.txt > nul 2>&1
echo.OK - Dependencies installed
echo.

REM Create directories
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "logs" mkdir logs
echo.OK - Directories created
echo.

REM Create .env if not exists
if not exist ".env" (
    copy .env.example .env > nul
    echo.OK - Created .env (please edit with your settings)
) else (
    echo.OK - .env already exists
)
echo.

REM Train model
if exist "data\pilot_roster.csv" if exist "data\missions.csv" (
    echo.Training ML model...
    python src\train_model.py data\pilot_roster.csv data\missions.csv
    echo.
)

echo.================================================
echo.  ^OK Setup Complete!
echo.================================================
echo.
echo.Next commands:
echo.1. Start API server:
echo.   python src\main.py
echo.
echo.2. In another terminal, test:
echo.   curl http://localhost:8000/health
echo.
echo.3. Visit documentation:
echo.   http://localhost:8000/docs
echo.
pause
