@echo off
cd /d "%~dp0"

echo ========================================
echo   Document Proofreader
echo ========================================
echo.
echo Starting server at http://127.0.0.1:5000
echo.

REM Open browser after short delay
start http://127.0.0.1:5000

REM Try to find and run Python
python --version >nul 2>&1
if %errorlevel%==0 (
    python src\app.py
    goto end
)

python3 --version >nul 2>&1
if %errorlevel%==0 (
    python3 src\app.py
    goto end
)

"D:\Program Files\Python312\python.exe" --version >nul 2>&1
if %errorlevel%==0 (
    "D:\Program Files\Python312\python.exe" src\app.py
    goto end
)

echo ERROR: Python not found!
echo Please install Python 3 from https://www.python.org/downloads/

:end
pause
