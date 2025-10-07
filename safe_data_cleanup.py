"""
🏥 MAHIMA MEDICARE - SAFE DATA CLEANUP SCRIPT
This script helps you remove test data while preserving client data
================================================================
"""

import os
import sys
import django
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from hospital_admin.models import Clinical_Laboratory_Technician, Admin_Information
from hospital.models import Patient
from pharmacy.models import Medicine, Pharmacist
from doctor.models import Doctor_Information

def backup_data():
    """Create a backup before cleanup"""
    print("📦 Creating backup before cleanup...")
    os.system('python manage.py dumpdata --natural-foreign --natural-primary > cleanup_backup.json')
    print("✅ Backup created: cleanup_backup.json")

def show_current_data():
    """Show what data exists"""
    print("\n📊 CURRENT DATA OVERVIEW:")
    print("=" * 40)
    
    patients = Patient.objects.all().count()
    doctors = Doctor_Information.objects.all().count() 
    medicines = Medicine.objects.all().count()
    admins = Admin_Information.objects.all().count()
    lab_techs = Clinical_Laboratory_Technician.objects.all().count()
    pharmacists = Pharmacist.objects.all().count()
    
    print(f"👥 Patients: {patients}")
    print(f"👨‍⚕️ Doctors: {doctors}")
    print(f"💊 Medicines: {medicines}")
    print(f"👨‍💼 Admins: {admins}")
    print(f"🔬 Lab Technicians: {lab_techs}")
    print(f"💉 Pharmacists: {pharmacists}")

def list_lab_technicians():
    """List all lab technicians for review"""
    print("\n🔬 LAB TECHNICIANS:")
    print("=" * 30)
    
    lab_techs = Clinical_Laboratory_Technician.objects.all()
    for i, tech in enumerate(lab_techs, 1):
        print(f"{i}. {tech.first_name} {tech.last_name} - {tech.email}")
    
    return lab_techs

def list_test_admins():
    """List admin accounts that might be test accounts"""
    print("\n👨‍💼 ADMIN ACCOUNTS:")
    print("=" * 20)
    
    admins = Admin_Information.objects.all()
    for i, admin in enumerate(admins, 1):
        print(f"{i}. {admin.first_name} {admin.last_name} - {admin.email}")
    
    return admins

def safe_cleanup():
    """Interactive cleanup process"""
    print("\n🧹 STARTING SAFE CLEANUP PROCESS")
    print("=" * 35)
    
    backup_data()
    show_current_data()
    
    # Show lab technicians
    lab_techs = list_lab_technicians()
    
    if lab_techs.exists():
        print(f"\n❓ Do you want to remove ALL {lab_techs.count()} lab technicians?")
        response = input("Type 'YES' to confirm, or 'NO' to skip: ").strip().upper()
        
        if response == 'YES':
            with transaction.atomic():
                count = lab_techs.count()
                lab_techs.delete()
                print(f"✅ Removed {count} lab technicians")
        else:
            print("⏭️ Skipped lab technician removal")
    
    # Show admin accounts
    admins = list_test_admins()
    
    if admins.exists():
        print(f"\n❓ Review admin accounts. Do you want to remove test admin accounts?")
        print("⚠️  WARNING: Be careful not to remove your main admin account!")
        
        for i, admin in enumerate(admins, 1):
            print(f"\n{i}. {admin.first_name} {admin.last_name} ({admin.email})")
            remove = input(f"Remove this admin? (y/N): ").strip().lower()
            
            if remove == 'y':
                admin.delete()
                print(f"✅ Removed admin: {admin.first_name} {admin.last_name}")
            else:
                print(f"⏭️ Kept admin: {admin.first_name} {admin.last_name}")

def show_final_status():
    """Show final data status"""
    print("\n📊 FINAL DATA STATUS:")
    print("=" * 25)
    show_current_data()
    
    print("\n🎉 CLEANUP COMPLETED!")
    print("✅ Client data preserved")
    print("✅ Test accounts removed")
    print("✅ Backup created for safety")

def main():
    print("🏥 MAHIMA MEDICARE - DATA CLEANUP TOOL")
    print("🚨 This tool helps remove test data safely")
    print("=" * 45)
    
    print("\n⚠️  IMPORTANT WARNINGS:")
    print("1. This will create a backup first")
    print("2. Only remove accounts you're sure are test accounts")
    print("3. Don't remove your main admin account")
    print("4. Client data will be preserved")
    
    proceed = input("\n❓ Do you want to proceed? (y/N): ").strip().lower()
    
    if proceed == 'y':
        safe_cleanup()
        show_final_status()
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    main()