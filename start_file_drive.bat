@echo off
echo ========================================
echo    File Drive - Starting Application
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting File Drive server...
echo.
echo The application will be available at:
echo http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python main.py
pause 