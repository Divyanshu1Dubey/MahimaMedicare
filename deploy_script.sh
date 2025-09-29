#!/bin/bash
# Auto-deployment script for Mahima Medicare
# This script will be called to update the website

echo "=== Starting Auto Deployment ==="
cd /var/www/mahima-medicare

echo "=== Pulling latest changes from GitHub ==="
git pull origin main

echo "=== Activating virtual environment ==="
source venv/bin/activate

echo "=== Installing/updating dependencies ==="
pip install -r requirements.txt

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Restarting Gunicorn ==="
pkill -f gunicorn || true
sleep 3

echo "=== Starting Gunicorn ==="
nohup gunicorn --config gunicorn.conf.py healthstack.wsgi:application > gunicorn.log 2>&1 &

echo "=== Deployment completed successfully! ==="
echo "=== Checking if Gunicorn is running ==="
sleep 3
ps aux | grep gunicorn | grep -v grep

echo "=== Testing website ==="
curl -I http://127.0.0.1:8000/ | head -1