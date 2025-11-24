@echo off
echo ========================================
echo Pushing to GitHub
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if repository is initialized
if not exist .git (
    echo ERROR: Git repository not initialized!
    echo Please run setup_git.bat first
    pause
    exit /b 1
)

echo Pushing to GitHub...
echo Repository: https://github.com/Phattarapong26/app.git
echo.
echo You will be prompted for credentials:
echo Username: Phattarapong26
echo Password: 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
echo.

REM Push to GitHub
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo Push failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Wrong credentials
    echo 2. Repository doesn't exist on GitHub
    echo 3. No internet connection
    echo 4. Branch protection rules
    echo.
    echo Try:
    echo - Check your GitHub token is valid
    echo - Make sure repository exists: https://github.com/Phattarapong26/app
    echo - Check internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Successfully pushed to GitHub!
echo ========================================
echo.
echo View your repository at:
echo https://github.com/Phattarapong26/app
echo.
pause
