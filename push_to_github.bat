@echo off
echo ========================================
echo    File Drive - GitHub Push Script
echo ========================================
echo.
echo This script will help you push your File Drive project to GitHub.
echo.
echo Please follow these steps:
echo 1. Create a repository named 'filedrive' on GitHub
echo 2. Get your GitHub username
echo 3. Run this script with your username
echo.
set /p username="Enter your GitHub username: "
echo.
echo Setting up remote repository...
git remote set-url origin https://github.com/%username%/filedrive.git
echo.
echo Pushing to GitHub...
git push -u origin main
echo.
echo ========================================
echo    Push Complete!
echo ========================================
echo.
echo Your repository is now available at:
echo https://github.com/%username%/filedrive
echo.
echo You can now:
echo - Share the repository with others
echo - Clone it on other machines
echo - Deploy it to cloud platforms
echo.
pause 