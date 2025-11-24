@echo off
echo ========================================
echo Dashboard Data Import Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Installing required packages...
pip install pandas sqlalchemy psycopg2-binary
echo.

echo ========================================
echo Starting Data Import...
echo ========================================
echo.

python import_all_dashboard_data.py

echo.
echo ========================================
echo Import Complete!
echo ========================================
pause
