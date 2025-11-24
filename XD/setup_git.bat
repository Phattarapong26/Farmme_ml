@echo off
echo ========================================
echo Setting up Git Repository
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Initialize Git repository
echo [1/6] Initializing Git repository...
git init
if errorlevel 1 (
    echo ERROR: Failed to initialize Git repository
    pause
    exit /b 1
)
echo Done!
echo.

REM Configure Git user (change these if needed)
echo [2/6] Configuring Git user...
git config user.name "Phattarapong26"
git config user.email "phattarapong26@example.com"
echo Done!
echo.

REM Add remote repository
echo [3/6] Adding remote repository...
git remote add origin https://github.com/Phattarapong26/app.git
if errorlevel 1 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/Phattarapong26/app.git
)
echo Done!
echo.

REM Add all files
echo [4/6] Adding files to Git...
git add .
echo Done!
echo.

REM Create initial commit
echo [5/6] Creating initial commit...
git commit -m "Initial commit: FarmMe project with Supabase migration

- Add backend API with FastAPI
- Add frontend with React
- Migrate database to Supabase cloud
- Add migration scripts and documentation
- Add setup guide for team members
- Configure .gitignore for security"
if errorlevel 1 (
    echo ERROR: Failed to create commit
    pause
    exit /b 1
)
echo Done!
echo.

REM Set main branch
echo [6/6] Setting up main branch...
git branch -M main
echo Done!
echo.

echo ========================================
echo Git repository setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Push to GitHub with: git push -u origin main
echo 2. You will be prompted for your GitHub credentials
echo    Username: Phattarapong26
echo    Password: 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
echo.
echo Or run: push_to_github.bat
echo.
pause
