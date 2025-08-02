@echo off
echo ========================================
echo    File Drive - Deployment Helper
echo ========================================
echo.
echo This script will help you prepare for deployment.
echo.
echo Step 1: Push to GitHub
echo.
git add .
git commit -m "Ready for deployment"
git push origin main
echo.
echo ========================================
echo    Deployment Options
echo ========================================
echo.
echo Choose your deployment platform:
echo.
echo 1. RENDER (Recommended - Easiest)
echo    - Go to: https://render.com
echo    - Sign up with GitHub
echo    - Click "New +" -> "Web Service"
echo    - Connect your repository
echo    - Deploy automatically
echo.
echo 2. RAILWAY (Alternative)
echo    - Go to: https://railway.app
echo    - Sign up with GitHub
echo    - Click "New Project"
echo    - Connect your repository
echo    - Deploy automatically
echo.
echo 3. VERCEL (Fastest)
echo    - Go to: https://vercel.com
echo    - Sign up with GitHub
echo    - Click "New Project"
echo    - Import your repository
echo    - Deploy automatically
echo.
echo ========================================
echo    Your App Will Be Live At:
echo ========================================
echo.
echo Render:     https://filedrive.onrender.com
echo Railway:    https://filedrive-production.up.railway.app
echo Vercel:     https://filedrive.vercel.app
echo.
echo ========================================
echo    Mobile Access:
echo ========================================
echo.
echo After deployment, your app will be:
echo - Available 24/7 from anywhere
echo - Mobile-optimized for all devices
echo - Secure with HTTPS
echo - PWA-ready for home screen installation
echo.
pause 