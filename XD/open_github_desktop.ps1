# Open GitHub Desktop and Show Instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Opening GitHub Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Try to open GitHub Desktop
$githubDesktopPaths = @(
    "$env:LOCALAPPDATA\GitHubDesktop\GitHubDesktop.exe",
    "$env:PROGRAMFILES\GitHub Desktop\GitHubDesktop.exe",
    "${env:PROGRAMFILES(x86)}\GitHub Desktop\GitHubDesktop.exe"
)

$found = $false
foreach ($path in $githubDesktopPaths) {
    if (Test-Path $path) {
        Write-Host "Found GitHub Desktop at: $path" -ForegroundColor Green
        Write-Host "Opening GitHub Desktop..." -ForegroundColor Yellow
        Start-Process $path
        $found = $true
        break
    }
}

if (-not $found) {
    Write-Host "GitHub Desktop not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install GitHub Desktop from:" -ForegroundColor Yellow
    Write-Host "https://desktop.github.com/" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Quick Setup Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Follow these steps in GitHub Desktop:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Login to GitHub" -ForegroundColor Green
Write-Host "   File -> Options -> Accounts -> Sign in" -ForegroundColor White
Write-Host "   Username: Phattarapong26" -ForegroundColor Cyan
Write-Host "   Token: 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" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Add This Repository" -ForegroundColor Green
Write-Host "   File -> Add local repository" -ForegroundColor White
Write-Host "   Choose: $PWD" -ForegroundColor Cyan
Write-Host "   If error -> Click create a repository" -ForegroundColor Yellow
Write-Host ""

Write-Host "3. Commit Changes" -ForegroundColor Green
Write-Host "   Summary: Initial commit: FarmMe project" -ForegroundColor Cyan
Write-Host "   Click: Commit to main" -ForegroundColor White
Write-Host ""

Write-Host "4. Publish to GitHub" -ForegroundColor Green
Write-Host "   Click: Publish repository" -ForegroundColor White
Write-Host "   Name: app" -ForegroundColor Cyan
Write-Host "   Organization: Phattarapong26" -ForegroundColor Cyan
Write-Host "   Click: Publish" -ForegroundColor White
Write-Host ""

Write-Host "5. Verify" -ForegroundColor Green
Write-Host "   Open: https://github.com/Phattarapong26/app" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Full guide: GITHUB_DESKTOP_GUIDE.md" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
