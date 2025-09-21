@echo off
echo Installing production dependencies...
pip install whitenoise==6.6.0
pip install gunicorn==21.2.0
pip install psycopg2-binary==2.9.9
pip install dj-database-url==2.1.0
echo Production dependencies installed successfully!
pause
