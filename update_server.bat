@echo off
echo Copying updated files to server...

REM Copy updated settings.py
scp -o "StrictHostKeyChecking=no" healthstack/settings.py root@139.84.155.25:/var/www/mahima-medicare/healthstack/

REM Copy updated .env file
scp -o "StrictHostKeyChecking=no" .env root@139.84.155.25:/var/www/mahima-medicare/

echo Files copied. Restarting services on server...

REM SSH and restart services
ssh -o "StrictHostKeyChecking=no" root@139.84.155.25 "cd /var/www/mahima-medicare && killall gunicorn && sleep 3 && source venv/bin/activate && gunicorn --config gunicorn.conf.py healthstack.wsgi:application --daemon"

echo Server updated and restarted!
echo Test your website at: http://139.84.155.25/