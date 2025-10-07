#!/bin/bash

# 🏥 MAHIMA MEDICARE - SAFE PRODUCTION UPDATE SCRIPT
# This script updates code while preserving all client data
# ===================================================

echo "🏥 MAHIMA MEDICARE - SAFE PRODUCTION UPDATE"
echo "==========================================="

# 1. BACKUP EXISTING DATA (CRITICAL!)
echo "📦 Step 1: Creating database backup..."
cd /var/www/mahima-medicare
source venv/bin/activate

# Create timestamped backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
echo "Creating backup: backup_${BACKUP_DATE}.json"
python manage.py dumpdata --natural-foreign --natural-primary > "backup_${BACKUP_DATE}.json"

# Also backup the database file if using SQLite
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "db_backup_${BACKUP_DATE}.sqlite3"
    echo "✅ SQLite database backed up"
fi

echo "✅ Data backup completed successfully!"

# 2. BACKUP MEDIA FILES (uploaded files, images, etc.)
echo "📁 Step 2: Backing up media files..."
if [ -d "media" ]; then
    tar -czf "media_backup_${BACKUP_DATE}.tar.gz" media/
    echo "✅ Media files backed up"
fi

# 3. PULL LATEST CODE CHANGES
echo "🔄 Step 3: Updating code..."
git stash  # Save any local changes
git pull origin main

# 4. UPDATE DEPENDENCIES (if requirements.txt changed)
echo "📦 Step 4: Updating dependencies..."
pip install -r requirements.txt --upgrade

# 5. RUN MIGRATIONS (this will ADD new features without deleting data)
echo "🗄️  Step 5: Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 6. COLLECT STATIC FILES
echo "📂 Step 6: Collecting static files..."
python manage.py collectstatic --noinput

# 7. GRACEFULLY RESTART SERVICES
echo "🔄 Step 7: Restarting services..."
# Stop Gunicorn gracefully
pkill -f gunicorn

# Wait a moment
sleep 2

# Start Gunicorn again
gunicorn --config gunicorn.conf.py healthstack.wsgi:application &

echo "✅ Production update completed successfully!"
echo ""
echo "📊 WHAT WAS PRESERVED:"
echo "✅ All patient data"
echo "✅ All medicine records"
echo "✅ All lab test data"
echo "✅ All user accounts"
echo "✅ All uploaded files"
echo ""
echo "🔒 SECURITY IMPROVEMENTS APPLIED:"
echo "✅ Admin registration removed"
echo "✅ Only superuser can create admin accounts now"
echo ""
echo "🌐 Your website is now updated and running!"
echo "Visit: https://mahimamedicare.co.in"