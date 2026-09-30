@echo off
echo ========================================================
echo   Starting EcoPulse Waste Management System (MVP)
echo ========================================================
echo.
echo Installing dependencies if needed...
python -m pip install -r requirements.txt
echo.
echo Starting application server on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
