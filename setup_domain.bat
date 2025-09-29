@echo off
echo Updating server configuration for domain mahimamedicare.co.in...

ssh root@139.84.155.25 "
# Update .env file with new domain
sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=mahimamedicare.co.in,www.mahimamedicare.co.in,139.84.155.25,127.0.0.1,localhost/' /var/www/mahima-medicare/.env

# Update Nginx configuration for domain
cat > /etc/nginx/sites-available/mahima-medicare << 'EOF'
server {
    listen 80;
    server_name mahimamedicare.co.in www.mahimamedicare.co.in 139.84.155.25;

    client_max_body_size 100M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
        return 204;
    }

    location /static/ {
        alias /var/www/mahima-medicare/staticfiles/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }

    location /media/ {
        alias /var/www/mahima-medicare/media/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Restart Gunicorn to load new ALLOWED_HOSTS
cd /var/www/mahima-medicare
source venv/bin/activate
killall gunicorn 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 3
gunicorn --config gunicorn.conf.py healthstack.wsgi:application &

echo 'Domain configuration updated!'
echo 'Your website will be accessible at:'
echo 'http://mahimamedicare.co.in'
echo 'http://www.mahimamedicare.co.in'
"

pause