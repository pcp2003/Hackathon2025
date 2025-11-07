@echo off
REM NaviAcess - One-Command Setup Script (Windows)
REM This script sets up both backend and frontend for development

echo.
echo =======================================
echo NaviAcess Setup Script (Windows)
echo =======================================
echo.

REM Check prerequisites
echo Checking prerequisites...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is required but not installed.
    exit /b 1
)

echo [OK] Python found: 
python --version

echo [OK] Node.js found: 
node --version

echo.

REM Backend Setup
echo =======================================
echo Setting up Backend...
echo =======================================

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo WARNING: Please edit backend\.env with your API keys
)

echo [OK] Backend setup complete

cd ..

echo.

REM Frontend Setup
echo =======================================
echo Setting up Frontend...
echo =======================================

cd frontend

echo Installing Node dependencies...
call npm install

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo [OK] Frontend setup complete

cd ..

echo.
echo =======================================
echo Setup Complete!
echo =======================================
echo.
echo Next steps:
echo 1. Update backend\.env with your API keys
echo 2. Run backend: cd backend && venv\Scripts\activate.bat && python main.py
echo 3. Run frontend: cd frontend && npm run dev
echo 4. Visit http://localhost:5173
echo.
pause
