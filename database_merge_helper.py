"""
🏥 MAHIMA MEDICARE - DATABASE MERGE HELPER
==========================================
This script helps you merge your local database with production data
"""

import json
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

def export_local_database():
    """Export current local database"""
    print("📤 Exporting local database...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"local_export_{timestamp}.json"
    
    os.system(f'python manage.py dumpdata --indent 2 > {filename}')
    print(f"✅ Local database exported to: {filename}")
    return filename

def show_local_data_summary():
    """Show summary of local data"""
    from hospital.models import Patient
    from doctor.models import Doctor_Information
    from pharmacy.models import Medicine
    from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician
    from django.contrib.auth.models import User
    
    print("\n📊 LOCAL DATABASE SUMMARY:")
    print("=" * 30)
    print(f"👥 Patients: {Patient.objects.count()}")
    print(f"👨‍⚕️ Doctors: {Doctor_Information.objects.count()}")
    print(f"💊 Medicines: {Medicine.objects.count()}")
    print(f"👨‍💼 Admins: {Admin_Information.objects.count()}")
    print(f"🔬 Lab Techs: {Clinical_Laboratory_Technician.objects.count()}")
    print(f"👤 Django Users: {User.objects.count()}")
    
    print("\n👤 DJANGO USERS:")
    for user in User.objects.all():
        print(f"  - {user.username} ({'superuser' if user.is_superuser else 'regular'})")

def create_production_commands():
    """Create SSH commands file for production"""
    commands = f"""#!/bin/bash
# 🏥 MAHIMA MEDICARE - PRODUCTION DATABASE BACKUP COMMANDS
# Execute these commands on your production server

echo "🏥 Backing up production database..."
cd /var/www/mahima-medicare
source venv/bin/activate

# Create timestamped backup
BACKUP_FILE="production_backup_$(date +%Y%m%d_%H%M%S).json"
python manage.py dumpdata --indent 2 > $BACKUP_FILE

echo "✅ Production backup created: $BACKUP_FILE"
echo "📥 Download this file to your local machine using:"
echo "scp root@139.84.155.25:/var/www/mahima-medicare/$BACKUP_FILE ./production_data.json"

# Also show current data summary
echo ""
echo "📊 PRODUCTION DATABASE SUMMARY:"
python manage.py shell << EOF
from hospital.models import Patient
from doctor.models import Doctor_Information
from pharmacy.models import Medicine
from hospital_admin.models import Admin_Information
from django.contrib.auth.models import User

print(f"👥 Patients: {{Patient.objects.count()}}")
print(f"👨‍⚕️ Doctors: {{Doctor_Information.objects.count()}}")
print(f"💊 Medicines: {{Medicine.objects.count()}}")
print(f"👨‍💼 Admins: {{Admin_Information.objects.count()}}")
print(f"👤 Django Users: {{User.objects.count()}}")
EOF
"""
    
    with open('production_backup_commands.sh', 'w') as f:
        f.write(commands)
    
    print("✅ Created production_backup_commands.sh")
    print("📤 Upload this file to your server and run it!")

def create_merge_strategy():
    """Create a merge strategy document"""
    strategy = """# 🏥 MAHIMA MEDICARE - DATABASE MERGE STRATEGY
===============================================

## OPTION 1: SIMPLE ADDITION (RECOMMENDED)
------------------------------------------
Instead of complex merging, simply ADD your data to production:

1. SSH to production: ssh root@139.84.155.25
2. Go to project: cd /var/www/mahima-medicare
3. Activate environment: source venv/bin/activate
4. Create superuser: python manage.py createsuperuser
5. Use admin panel to add:
   - Your medicines via: https://mahimamedicare.co.in/admin/
   - Your admin accounts
   - Any test data you need

## OPTION 2: FULL DATABASE REPLACEMENT
--------------------------------------
If you want to replace everything:

1. Backup production first!
2. Export your local database
3. Upload and load into production
4. Client will need to re-add their data

## OPTION 3: SELECTIVE DATA IMPORT
----------------------------------
Import only specific models:

```bash
# Export only specific data from local
python manage.py dumpdata pharmacy.medicine > medicines.json
python manage.py dumpdata hospital_admin.admin_information > admins.json

# Upload to production and load
python manage.py loaddata medicines.json
python manage.py loaddata admins.json
```

## RECOMMENDED APPROACH:
========================
Use OPTION 1 - it's safest and preserves all client data!
"""
    
    with open('DATABASE_MERGE_STRATEGY.md', 'w') as f:
        f.write(strategy)
    
    print("✅ Created DATABASE_MERGE_STRATEGY.md")

def main():
    print("🏥 MAHIMA MEDICARE - DATABASE MERGE HELPER")
    print("=========================================")
    
    show_local_data_summary()
    
    print("\n❓ What would you like to do?")
    print("1. Export local database for manual upload")
    print("2. Create production backup commands")
    print("3. Show merge strategy options")
    print("4. All of the above")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1" or choice == "4":
        export_local_database()
    
    if choice == "2" or choice == "4":
        create_production_commands()
    
    if choice == "3" or choice == "4":
        create_merge_strategy()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run the production backup commands on your server")
    print("2. Download production database")
    print("3. Choose your merge strategy")
    print("4. Execute the merge")
    print("\n🔒 Remember: Always backup before making changes!")

if __name__ == "__main__":
    main()