#!/bin/bash
# Simple one-command deployment for server
# Usage: ./one_click_deploy.sh

echo "🚀 Mahima Medicare - One Click Deployment"
echo "========================================"

# Set project directory
cd /var/www/mahima-medicare

# Backup current database
echo "📦 Backing up database..."
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3 2>/dev/null || echo "No existing database to backup"

# Export current data
echo "💾 Exporting current data..."
source venv/bin/activate
python export_data.py 2>/dev/null || echo "No data to export"

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Updating database..."
python manage.py makemigrations
python manage.py migrate

# Import data back
echo "📤 Restoring data..."
python import_data.py 2>/dev/null || echo "No data to restore"

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Restart application
echo "🔄 Restarting application..."
pkill -f gunicorn || true
sleep 2
nohup gunicorn --config gunicorn.conf.py healthstack.wsgi:application &

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your website is live at: https://mahimamedicare.com"
echo ""
echo "🆕 New features available:"
echo "   • Patients can upload prescription images"
echo "   • Pharmacists can review and process prescriptions"
echo "   • Automatic data backup and restore"
echo "   • Clean, optimized deployment"
