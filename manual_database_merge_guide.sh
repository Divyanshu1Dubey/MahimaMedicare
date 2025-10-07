#!/bin/bash

# 🏥 MAHIMA MEDICARE - MANUAL DATABASE MERGE GUIDE
# ===============================================
# This guide shows how to manually merge your local database 
# with production database via SSH

echo "🏥 MAHIMA MEDICARE - MANUAL DATABASE MERGE"
echo "=========================================="

# STEP 1: BACKUP PRODUCTION DATABASE
echo "📦 STEP 1: Backup Production Database"
echo "====================================="
echo "SSH Command:"
echo "ssh root@139.84.155.25"
echo ""
echo "Once connected, run:"
echo "cd /var/www/mahima-medicare"
echo "source venv/bin/activate"
echo "python manage.py dumpdata --indent 2 > production_backup_$(date +%Y%m%d_%H%M%S).json"
echo ""

# STEP 2: DOWNLOAD PRODUCTION DATABASE
echo "📥 STEP 2: Download Production Database to Local"
echo "=============================================="
echo "From your local machine:"
echo "scp root@139.84.155.25:/var/www/mahima-medicare/production_backup_*.json ./production_data.json"
echo ""

# STEP 3: EXPORT YOUR LOCAL DATABASE
echo "📤 STEP 3: Export Your Local Database"
echo "===================================="
echo "From your local project directory:"
echo "python manage.py dumpdata --indent 2 > local_data.json"
echo ""

# STEP 4: MERGE DATABASES
echo "🔄 STEP 4: Manual Database Merge Process"
echo "======================================="
echo "This requires careful manual work:"
echo ""
echo "A) Load production data into a temporary local database:"
echo "   python manage.py loaddata production_data.json"
echo ""
echo "B) Create your superuser and add your test data:"
echo "   python manage.py createsuperuser"
echo "   # Add medicines, admin accounts, etc. via admin panel"
echo ""
echo "C) Export the merged database:"
echo "   python manage.py dumpdata --indent 2 > merged_data.json"
echo ""

# STEP 5: UPLOAD MERGED DATABASE
echo "📤 STEP 5: Upload Merged Database"
echo "================================"
echo "Upload merged database to production:"
echo "scp merged_data.json root@139.84.155.25:/var/www/mahima-medicare/"
echo ""

# STEP 6: APPLY TO PRODUCTION
echo "🚀 STEP 6: Apply Merged Database to Production"
echo "============================================="
echo "SSH back into production:"
echo "ssh root@139.84.155.25"
echo "cd /var/www/mahima-medicare"
echo "source venv/bin/activate"
echo ""
echo "# Backup current database one more time"
echo "cp db.sqlite3 db_final_backup.sqlite3"
echo ""
echo "# Clear existing database (CAREFUL!)"
echo "python manage.py flush --noinput"
echo ""
echo "# Load merged data"
echo "python manage.py loaddata merged_data.json"
echo ""
echo "# Run migrations to ensure schema is up to date"
echo "python manage.py migrate"
echo ""
echo "# Restart server"
echo "pkill -f gunicorn"
echo "gunicorn --config gunicorn.conf.py healthstack.wsgi:application &"
echo ""

echo "✅ MERGE COMPLETED!"