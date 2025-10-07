#!/usr/bin/env python3
"""
Create Lab Technician User and Profile
Fixes the DoesNotExist error for Clinical_Laboratory_Technician
"""

import os
import sys
import django

# Setup Django
project_root = r"C:\Users\DIVYANSHU\MahimaMedicare"
sys.path.insert(0, project_root)
os.chdir(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from hospital.models import User
from hospital_admin.models import Clinical_Laboratory_Technician

def create_lab_technician():
    """Create a lab technician user and profile"""
    
    # Check if lab technician user exists
    lab_user = User.objects.filter(username='labtech@mahimamedicare.com').first()
    
    if not lab_user:
        print("Creating lab technician user...")
        lab_user = User.objects.create_user(
            username='labtech@mahimamedicare.com',
            email='labtech@mahimamedicare.com',
            password='labtech123',
            first_name='Lab',
            last_name='Technician'
        )
        
        # Mark as staff for admin access
        lab_user.is_staff = True
        lab_user.save()
        
        print(f"✅ Created lab technician user: {lab_user.username}")
    else:
        print(f"⚠️ Lab technician user already exists: {lab_user.username}")
    
    # Check if Clinical_Laboratory_Technician profile exists
    lab_tech_profile = Clinical_Laboratory_Technician.objects.filter(user=lab_user).first()
    
    if not lab_tech_profile:
        print("Creating Clinical_Laboratory_Technician profile...")
        lab_tech_profile = Clinical_Laboratory_Technician.objects.create(
            user=lab_user,
            name='Lab Technician',
            username='labtech',
            email='labtech@mahimamedicare.com',
            phone_number=9876543210,
            age=30
        )
        print(f"✅ Created lab technician profile: {lab_tech_profile.name}")
    else:
        print(f"⚠️ Lab technician profile already exists: {lab_tech_profile.name}")
    
    return lab_user, lab_tech_profile

def update_any_existing_user():
    """Update any existing user to be a lab worker as fallback"""
    
    # Get the first user and make them a lab worker for testing
    first_user = User.objects.first()
    
    if first_user:
        print(f"\nUpdating user {first_user.username} to be a lab worker...")
        
        # Mark as staff for admin access
        first_user.is_staff = True
        first_user.save()
        
        # Create lab tech profile if doesn't exist
        lab_tech_profile = Clinical_Laboratory_Technician.objects.filter(user=first_user).first()
        
        if not lab_tech_profile:
            lab_tech_profile = Clinical_Laboratory_Technician.objects.create(
                user=first_user,
                name=f'{first_user.first_name} {first_user.last_name}' or 'Lab Technician',
                username=first_user.username,
                email=first_user.email,
                phone_number=9876543210,
                age=30
            )
            print(f"✅ Created lab profile for user: {first_user.username}")
        
        return first_user, lab_tech_profile
    
    return None, None

if __name__ == "__main__":
    print("🏥 Mahima Medicare - Lab Technician Setup")
    print("=" * 50)
    
    try:
        # Try to create dedicated lab technician
        lab_user, lab_profile = create_lab_technician()
        
        # Also update first user as fallback
        backup_user, backup_profile = update_any_existing_user()
        
        print(f"\n📊 Summary:")
        print(f"Total users: {User.objects.count()}")
        print(f"Total lab technicians: {Clinical_Laboratory_Technician.objects.count()}")
        
        print(f"\n🔐 Lab Technician Login:")
        print(f"Username: labtech@mahimamedicare.com")
        print(f"Password: labtech123")
        
        print(f"\n✅ Lab dashboard should now work!")
        print(f"URL: http://localhost:8000/hospital_admin/labworker-dashboard/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()