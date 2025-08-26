@echo off
echo Starting Django Backend...
cd /d D:\backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start Gunicorn
echo Starting Gunicorn server...
gunicorn --config gunicorn.conf.py backend.wsgi:application

pause
