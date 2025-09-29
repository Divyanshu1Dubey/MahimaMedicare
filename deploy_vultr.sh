#!/bin/bash
# Simple Vultr Deployment Script for Mahima Medicare
# Run this on your Vultr server (Ubuntu/CentOS)

echo "🚀 Starting Mahima Medicare deployment on Vultr..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# Create application directory
sudo mkdir -p /var/www/mahima-medicare
cd /var/www/mahima-medicare

# Clone the repository
sudo git clone https://github.com/Divyanshu1Dubey/MahimaMedicare.git .

# Set up virtual environment
sudo python3 -m venv venv
sudo chown -R www-data:www-data /var/www/mahima-medicare

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Create production environment file
cat > .env << 'EOF'
# Production settings
SECRET_KEY=mahima-medicare-vultr-production-key-2025-change-this-to-random-string
DEBUG=False

# Database (SQLite for simplicity)
DATABASE_URL=sqlite:///./db.sqlite3

# Email backend (console for now, change to SMTP later)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Allowed hosts
ALLOWED_HOSTS=139.84.155.25,your-domain.com

# Razorpay (use your real keys)
RAZORPAY_KEY_ID=rzp_live_your_live_key
RAZORPAY_KEY_SECRET=your_live_secret_key
EOF

# Run database setup
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py init_db

# Create superuser (optional)
echo "from hospital.models import User; User.objects.create_superuser('admin', 'admin@mahimamedicare.com', 'mahima2025')" | python manage.py shell

# Set up Gunicorn
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# Create systemd service for Gunicorn
sudo tee /etc/systemd/system/mahima-medicare.service > /dev/null << 'EOF'
[Unit]
Description=Mahima Medicare Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mahima-medicare
Environment="PATH=/var/www/mahima-medicare/venv/bin"
ExecStart=/var/www/mahima-medicare/venv/bin/gunicorn --config gunicorn.conf.py healthstack.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mahima-medicare
sudo systemctl start mahima-medicare

# Configure Nginx
sudo tee /etc/nginx/sites-available/mahima-medicare > /dev/null << 'EOF'
server {
    listen 80;
    server_name 139.84.155.25;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/mahima-medicare/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/mahima-medicare/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/mahima-medicare /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# Open firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ Deployment completed!"
echo "🌐 Your website should be available at: http://139.84.155.25/"
echo "👤 Admin login: http://139.84.155.25/admin/"
echo "   Username: admin"
echo "   Password: mahima2025"
echo ""
echo "🔧 To check status:"
echo "   sudo systemctl status mahima-medicare"
echo "   sudo systemctl status nginx"
echo ""
echo "📋 To view logs:"
echo "   sudo journalctl -u mahima-medicare -f"
echo "   sudo tail -f /var/log/nginx/error.log"