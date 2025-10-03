#!/usr/bin/env python
"""Check existing lab technician users"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from hospital_admin.models import Clinical_Laboratory_Technician
from hospital.models import User

print("🔍 CHECKING EXISTING LAB TECHNICIAN USERS")
print("=" * 50)

# Check Clinical_Laboratory_Technician objects
lab_techs = Clinical_Laboratory_Technician.objects.all()
print(f"Lab Technicians in database: {lab_techs.count()}")

for lt in lab_techs:
    print(f"  - Name: {lt.name}")
    print(f"    Username: {lt.user.username if lt.user else 'No user'}")
    print(f"    Email: {lt.email}")
    print(f"    User ID: {lt.user.id if lt.user else 'N/A'}")
    if lt.user:
        print(f"    Is lab worker: {lt.user.is_labworker}")
        print(f"    Is active: {lt.user.is_active}")
    print()

# Check Users with is_labworker flag
print(f"\nUsers with is_labworker=True: {User.objects.filter(is_labworker=True).count()}")

for user in User.objects.filter(is_labworker=True):
    print(f"  - Username: {user.username}")
    print(f"    Name: {user.first_name} {user.last_name}")
    print(f"    Email: {user.email}")
    print(f"    Is active: {user.is_active}")
    print()

# Test password for user 'l1'
try:
    user = User.objects.get(username='l1')
    print(f"\nTesting user 'l1':")
    print(f"  - Has usable password: {user.has_usable_password()}")
    print(f"  - Password hash: {user.password[:20]}...")
    
    # Try to set a known password
    user.set_password('12345')
    user.save()
    print("  - Password reset to '12345' for testing")
    
except User.DoesNotExist:
    print("\nUser 'l1' not found")