@echo off
echo Deploying Django Backend to Production...
cd /d D:\backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run database migrations
echo Running migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Create logs directory
if not exist "logs" mkdir logs

echo Deployment completed!
echo.
echo Next steps:
echo 1. Update your domain in backend/settings_production.py
echo 2. Update your domain in nginx.conf
echo 3. Get SSL certificates for your domain
echo 4. Start the backend with: start_backend.bat
echo.
pause
