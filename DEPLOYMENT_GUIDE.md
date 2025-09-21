# 🚀 Mahima Medicare - Production Deployment Guide

## 🔧 Recent Fixes Applied

### ✅ Issues Resolved:
1. **Invoice Generation Error**: Fixed `'Cart' object has no attribute 'medicine'` error
   - Updated `razorpay_payment/invoice_utils.py` to use correct field name `order_item.item` instead of `order_item.medicine`
   
2. **Render.com Deployment Error**: Fixed missing `STATIC_ROOT` setting
   - Added `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` to settings.py
   - Added WhiteNoise middleware for static file serving
   - Added `.onrender.com` to `ALLOWED_HOSTS`
   - Created `build.sh` script for automated deployment
   
3. **Production Dependencies**: Added required packages
   - `gunicorn==21.2.0` - WSGI server for production
   - `whitenoise==6.6.0` - Static file serving
   - `psycopg2-binary==2.9.9` - PostgreSQL adapter
   - `dj-database-url==2.1.0` - Database URL parsing

### ✅ Security Enhancements:
- Added production security settings (HTTPS redirect, secure cookies, XSS protection)
- Configured WhiteNoise for efficient static file serving
- Added database configuration for both development and production

## 🚀 Quick Render.com Deployment

### Environment Variables to Set in Render.com:
```env
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
STORE_ID=your-store-id
STORE_PASSWORD=your-store-password
STORE_NAME=your-store-name
DATABASE_URL=postgresql://user:password@host:port/database
```

### Build Command:
```bash
./build.sh
```

### Start Command:
```bash
gunicorn healthstack.wsgi:application
```

## 📋 Pre-Deployment Checklist

### ✅ System Requirements
- **Python**: 3.8 or higher
- **Database**: PostgreSQL 12+ (recommended) or SQLite for development
- **Web Server**: Nginx + Gunicorn (recommended)
- **SSL Certificate**: Required for production
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 10GB free space

### ✅ Environment Setup

1. **Create Production Environment File**
```bash
cp .env.example .env.production
```

2. **Update Production Environment Variables**
```env
# Security
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DB_NAME=mahima_medicare_prod
DB_USER=mahima_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Payment Gateway
RAZORPAY_KEY_ID=your-production-razorpay-key
RAZORPAY_KEY_SECRET=your-production-razorpay-secret

# SSL Commerce (if using)
STORE_ID=your-store-id
STORE_PASSWORD=your-store-password
```

## 🔧 Production Setup Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib redis-server -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Database Setup (PostgreSQL)

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE mahima_medicare_prod;
CREATE USER mahima_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE mahima_medicare_prod TO mahima_user;
ALTER USER mahima_user CREATEDB;
\q
```

### 3. Application Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/mahima-medicare.git
cd mahima-medicare

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Set production settings
export DJANGO_SETTINGS_MODULE=healthstack.settings_production

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 4. Gunicorn Configuration

Create `/etc/systemd/system/mahima-medicare.service`:

```ini
[Unit]
Description=Mahima Medicare Healthcare System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/mahima-medicare
Environment="DJANGO_SETTINGS_MODULE=healthstack.settings_production"
ExecStart=/path/to/mahima-medicare/venv/bin/gunicorn --workers 3 --bind unix:/path/to/mahima-medicare/mahima.sock healthstack.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mahima-medicare
sudo systemctl start mahima-medicare
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/mahima-medicare`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/mahima-medicare;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /path/to/mahima-medicare;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/mahima-medicare/mahima.sock;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    location /login/ {
        limit_req zone=login burst=5 nodelay;
        include proxy_params;
        proxy_pass http://unix:/path/to/mahima-medicare/mahima.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mahima-medicare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate Setup

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Database Security

```bash
# Secure PostgreSQL
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_secure_password';"

# Edit pg_hba.conf to use md5 authentication
sudo nano /etc/postgresql/12/main/pg_hba.conf
# Change 'local all postgres peer' to 'local all postgres md5'

sudo systemctl restart postgresql
```

### 3. Application Security

Update `healthstack/settings_production.py`:

```python
# Additional security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Add security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'healthstack.middleware.SecurityMiddleware',
    'healthstack.middleware.SessionSecurityMiddleware',
    # ... other middleware
]
```

## 📊 Monitoring & Maintenance

### 1. Setup Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-mahima.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/mahima-medicare"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U mahima_user -h localhost mahima_medicare_prod > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/mahima-medicare/media/

# Remove old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-mahima.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-mahima.sh >> /var/log/mahima-backup.log 2>&1
```

### 2. Health Monitoring

```bash
# Add health check cron job
# Every 5 minutes
*/5 * * * * cd /path/to/mahima-medicare && /path/to/mahima-medicare/venv/bin/python manage.py system_health_check --email >> /var/log/mahima-health.log 2>&1
```

### 3. Log Rotation

Create `/etc/logrotate.d/mahima-medicare`:

```
/path/to/mahima-medicare/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload mahima-medicare
    endscript
}
```

## 🚨 Emergency Procedures

### 1. Quick Rollback

```bash
# Stop services
sudo systemctl stop mahima-medicare

# Restore from backup
pg_dump -U mahima_user -h localhost mahima_medicare_prod < /backups/mahima-medicare/db_YYYYMMDD_HHMMSS.sql

# Restart services
sudo systemctl start mahima-medicare
```

### 2. Maintenance Mode

```bash
# Enable maintenance mode
cd /path/to/mahima-medicare
echo "MAINTENANCE_MODE = True" >> healthstack/settings_production.py

# Restart application
sudo systemctl restart mahima-medicare
```

### 3. Performance Issues

```bash
# Check system resources
htop
df -h
free -m

# Check application logs
sudo journalctl -u mahima-medicare -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_report_patient_status ON doctor_report(patient_id, status);
CREATE INDEX idx_appointment_date_status ON doctor_appointment(appointment_date, appointment_status);
CREATE INDEX idx_payment_patient_status ON razorpay_payment_razorpaypayment(patient_id, status);
```

### 2. Caching Setup (Redis)

```python
# Add to settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## 🔍 Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --clear
   sudo systemctl restart nginx
   ```

2. **Database connection errors**
   ```bash
   sudo systemctl status postgresql
   sudo -u postgres psql -c "SELECT version();"
   ```

3. **Permission errors**
   ```bash
   sudo chown -R www-data:www-data /path/to/mahima-medicare
   sudo chmod -R 755 /path/to/mahima-medicare
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew
   ```

## 📞 Support Contacts

- **Technical Support**: tech@mahimamedicare.com
- **Emergency Contact**: +91 9348221721
- **System Administrator**: admin@mahimamedicare.com

---

## ✅ Post-Deployment Verification

After deployment, verify these endpoints:

- [ ] `https://yourdomain.com/` - Home page loads
- [ ] `https://yourdomain.com/login/` - Login page works
- [ ] `https://yourdomain.com/admin/` - Admin panel accessible
- [ ] `https://yourdomain.com/api/health/` - Health check returns 200
- [ ] SSL certificate is valid and secure
- [ ] All static files load correctly
- [ ] Email notifications work
- [ ] Payment gateway integration works
- [ ] Database backups are created successfully

**🎉 Congratulations! Mahima Medicare Healthcare System is now live in production!**
