# 🚀 Mahima Medicare - Vultr Deployment Guide

## Server Details
- **IP Address**: 139.84.155.25
- **Password**: D_o5{e2vYDL7fAR#

## Option 1: Simple Direct Deployment (Recommended)

### Step 1: Connect to your Vultr server
```bash
ssh root@139.84.155.25
# Enter password: D_o5{e2vYDL7fAR#
```

### Step 2: Download and run deployment script
```bash
# Download the deployment script
wget https://raw.githubusercontent.com/Divyanshu1Dubey/MahimaMedicare/main/deploy_vultr.sh

# Make it executable
chmod +x deploy_vultr.sh

# Run the deployment
./deploy_vultr.sh
```

### Step 3: Access your website
- **Website**: http://139.84.155.25/
- **Admin Panel**: http://139.84.155.25/admin/
- **Username**: admin
- **Password**: mahima2025

---

## Option 2: Docker Deployment (Alternative)

### Step 1: Connect to server and install Docker
```bash
ssh root@139.84.155.25

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone and deploy
```bash
# Clone repository
git clone https://github.com/Divyanshu1Dubey/MahimaMedicare.git
cd MahimaMedicare

# Build and run with Docker
docker-compose up -d --build
```

---

## Post-Deployment Tasks

### 1. Check service status
```bash
sudo systemctl status mahima-medicare
sudo systemctl status nginx
```

### 2. View logs
```bash
# Django app logs
sudo journalctl -u mahima-medicare -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. Restart services if needed
```bash
sudo systemctl restart mahima-medicare
sudo systemctl restart nginx
```

### 4. Update application
```bash
cd /var/www/mahima-medicare
sudo git pull origin main
sudo systemctl restart mahima-medicare
```

---

## Security Recommendations

### 1. Change default passwords
- Admin password: mahima2025 → Change this immediately
- SSH key authentication instead of password

### 2. Set up SSL certificate (Optional - costs extra)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com
```

### 3. Regular backups
```bash
# Backup database
cp /var/www/mahima-medicare/db.sqlite3 /backup/db_$(date +%Y%m%d).sqlite3

# Backup media files
tar -czf /backup/media_$(date +%Y%m%d).tar.gz /var/www/mahima-medicare/media/
```

---

## Troubleshooting

### Common Issues:

1. **502 Bad Gateway**
   - Check if Gunicorn is running: `sudo systemctl status mahima-medicare`
   - Restart service: `sudo systemctl restart mahima-medicare`

2. **Static files not loading**
   - Run: `cd /var/www/mahima-medicare && python manage.py collectstatic --noinput`
   - Restart Nginx: `sudo systemctl restart nginx`

3. **Database errors**
   - Run migrations: `cd /var/www/mahima-medicare && python manage.py migrate`
   - Initialize database: `python manage.py init_db`

### Performance Monitoring:
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check CPU usage
htop
```

---

## Cost Optimization

✅ **Low-cost setup** - Uses SQLite database (no additional DB costs)
✅ **Minimal resources** - Runs on basic Vultr instance
✅ **No external services** - Self-contained deployment

**Estimated Monthly Cost**: $5-10 USD (basic Vultr VPS only)

---

## Support Commands

### Emergency restart everything:
```bash
sudo systemctl restart mahima-medicare nginx
```

### Complete redeployment:
```bash
cd /var/www/mahima-medicare
sudo git pull origin main
sudo systemctl restart mahima-medicare
```

### Check everything is working:
```bash
curl -I http://139.84.155.25/
```

---

**🎉 Your Mahima Medicare website should now be live at http://139.84.155.25/**