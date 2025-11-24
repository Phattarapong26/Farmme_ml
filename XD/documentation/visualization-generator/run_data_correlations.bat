@echo off
REM FarmMe Data Correlation Analyzer
REM Batch script to generate correlation heatmaps

echo ========================================
echo FarmMe Data Correlation Analyzer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Installing/checking dependencies...
pip install -q matplotlib seaborn pandas numpy

echo.
echo Running correlation analyzer...
echo.

python generate_data_correlations.py

if errorlevel 1 (
    echo.
    echo ERROR: Correlation analysis failed
    echo Check the log for details
) else (
    echo.
    echo SUCCESS: All correlation heatmaps generated
    echo Check outputs/data_correlations folder
)

echo.
pause
