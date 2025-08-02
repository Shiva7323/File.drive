# File Drive - GitHub Push Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "   File Drive - GitHub Push Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "This script will help you push your File Drive project to GitHub." -ForegroundColor Yellow
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host "1. Create a repository named 'filedrive' on GitHub" -ForegroundColor White
Write-Host "2. Get your GitHub username" -ForegroundColor White
Write-Host "3. Enter your username when prompted" -ForegroundColor White
Write-Host ""

$username = Read-Host "Enter your GitHub username"
Write-Host ""

Write-Host "Setting up remote repository..." -ForegroundColor Cyan
git remote set-url origin "https://github.com/$username/filedrive.git"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Push Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your repository is now available at:" -ForegroundColor Yellow
Write-Host "https://github.com/$username/filedrive" -ForegroundColor White
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "- Share the repository with others" -ForegroundColor White
Write-Host "- Clone it on other machines" -ForegroundColor White
Write-Host "- Deploy it to cloud platforms" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue" 