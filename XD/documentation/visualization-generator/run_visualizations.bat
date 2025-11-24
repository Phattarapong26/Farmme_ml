@echo off
REM FarmMe Visualization Generator
REM Batch script to run visualization generation

echo ========================================
echo FarmMe Visualization Generator
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
pip install -q matplotlib seaborn pandas numpy scikit-learn Pillow xgboost scipy

echo.
echo Running visualization generator...
echo.

python generate_all_visualizations.py

if errorlevel 1 (
    echo.
    echo ERROR: Visualization generation failed
    echo Check the log file for details
) else (
    echo.
    echo SUCCESS: All visualizations generated
    echo Check the outputs folder for results
)

echo.
pause
