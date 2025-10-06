# 🚀 Vultr Server Deployment Guide

## Quick Deployment Commands

### 1. Connect and Setup
```bash
# Connect to your server
ssh root@139.84.155.25

# First time setup (if needed)
cd /var/www
git clone https://github.com/Divyanshu1Dubey/MahimaMedicare.git mahima-medicare
cd mahima-medicare

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env file
cp .env.example .env
# Edit .env with your production values:
# nano .env
```

### 2. Database Setup (First Time Only)
```bash
cd /var/www/mahima-medicare
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. Regular Deployment (Your Commands)
```bash
# Connect to server
ssh root@139.84.155.25

# Go to project directory
cd /var/www/mahima-medicare

# Pull latest changes from GitHub
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Run migrations for database changes
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn to apply changes
killall gunicorn || true
pkill -f gunicorn || true
gunicorn --config gunicorn.conf.py healthstack.wsgi:application &
```

### 4. Gunicorn Configuration

Create `/var/www/mahima-medicare/gunicorn.conf.py`:
```python
bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = True
pidfile = "/var/run/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"
```

### 5. Production Environment Variables

Your `/var/www/mahima-medicare/.env` should have:
```bash
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
ALLOWED_HOSTS=139.84.155.25,your-domain.com,mahimamedicare.com
DATABASE_URL=sqlite:///db.sqlite3
RAZORPAY_KEY_ID=your-production-razorpay-key
RAZORPAY_KEY_SECRET=your-production-razorpay-secret
```

### 6. Nginx Configuration (Optional)

If using Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name 139.84.155.25 your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/mahima-medicare/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/mahima-medicare/media/;
        expires 30d;
    }
}
```

### 7. Troubleshooting

Check if Gunicorn is running:
```bash
ps aux | grep gunicorn
```

Check logs:
```bash
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log
```

Test the application:
```bash
curl http://127.0.0.1:8000
```

### 8. One-Command Deployment Script

Create `/var/www/deploy.sh`:
```bash
#!/bin/bash
cd /var/www/mahima-medicare
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
killall gunicorn || true
pkill -f gunicorn || true
sleep 2
gunicorn --config gunicorn.conf.py healthstack.wsgi:application &
echo "Deployment complete!"
```

Then just run:
```bash
ssh root@139.84.155.25 'bash /var/www/deploy.sh'
```