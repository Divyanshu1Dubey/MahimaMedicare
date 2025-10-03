#!/usr/bin/env python3
"""
Simple Lab Technician Registration Test
"""

import os
import sys
import django
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from hospital.models import User
from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician
from hospital_admin.forms import LabWorkerCreationForm

def test_simple_registration():
    """Simple test of registration functionality"""
    print("SIMPLE LAB TECHNICIAN REGISTRATION TEST")
    print("=" * 50)
    
    client = Client()
    
    # Find existing admin user
    try:
        admin_user = User.objects.filter(is_hospital_admin=True).first()
        if not admin_user:
            print("No admin user found, creating one...")
            admin_user = User.objects.create_user(
                username='test_admin',
                email='admin@test.com',
                password='testpass123',
                is_hospital_admin=True
            )
            print(f"✓ Admin user created: {admin_user.username}")
        else:
            print(f"✓ Using existing admin user: {admin_user.username}")
            
        # Login as admin
        login_success = client.login(username=admin_user.username, password='testpass123')
        if not login_success:
            # Try with a known password
            admin_user.set_password('testpass123')
            admin_user.save()
            login_success = client.login(username=admin_user.username, password='testpass123')
        
        if login_success:
            print("✓ Admin logged in successfully")
        else:
            print("✗ Failed to login as admin")
            return False
            
    except Exception as e:
        print(f"✗ Error with admin setup: {e}")
        return False
    
    # Test form creation
    print("\n--- Testing Form ---")
    form_data = {
        'username': 'test_lab_tech_new',
        'email': 'testlabtech@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    
    form = LabWorkerCreationForm(data=form_data)
    if form.is_valid():
        print("✓ Form is valid")
        
        # Test form save
        try:
            user = form.save(commit=False)
            user.is_labworker = True
            user.save()
            print(f"✓ User saved: {user.username}")
            
            # Check if Clinical_Laboratory_Technician was created
            try:
                lab_tech = Clinical_Laboratory_Technician.objects.get(user=user)
                print(f"✓ Lab technician profile created: {lab_tech}")
                return True
            except Clinical_Laboratory_Technician.DoesNotExist:
                print("✗ Lab technician profile NOT created - Signal issue!")
                return False
                
        except Exception as e:
            print(f"✗ Error saving user: {e}")
            return False
    else:
        print(f"✗ Form is invalid: {form.errors}")
        return False

def test_view_registration():
    """Test the actual view registration"""
    print("\n--- Testing View Registration ---")
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_hospital_admin=True).first()
    if not admin_user:
        print("✗ No admin user found")
        return False
    
    # Ensure password is set
    admin_user.set_password('testpass123')
    admin_user.save()
    
    # Login
    if not client.login(username=admin_user.username, password='testpass123'):
        print("✗ Failed to login")
        return False
    
    print("✓ Admin logged in for view test")
    
    # Count before
    users_before = User.objects.count()
    lab_techs_before = Clinical_Laboratory_Technician.objects.count()
    print(f"Before: Users={users_before}, Lab Techs={lab_techs_before}")
    
    # Test POST to view
    form_data = {
        'username': 'view_test_lab_tech',
        'email': 'viewtest@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    
    response = client.post(reverse('add-lab-worker'), data=form_data)
    print(f"POST response status: {response.status_code}")
    
    # Count after
    users_after = User.objects.count()
    lab_techs_after = Clinical_Laboratory_Technician.objects.count()
    print(f"After: Users={users_after}, Lab Techs={lab_techs_after}")
    
    # Check if redirect happened (success)
    if response.status_code == 302:
        print("✓ Registration successful (redirect occurred)")
        
        # Verify user was created
        try:
            new_user = User.objects.get(username='view_test_lab_tech')
            print(f"✓ User created: {new_user.username}, is_labworker: {new_user.is_labworker}")
            
            # Check lab tech profile
            try:
                lab_tech = Clinical_Laboratory_Technician.objects.get(user=new_user)
                print(f"✓ Lab technician profile: {lab_tech}")
                return True
            except Clinical_Laboratory_Technician.DoesNotExist:
                print("✗ Lab technician profile missing!")
                return False
                
        except User.DoesNotExist:
            print("✗ User was not created!")
            return False
    else:
        print(f"✗ Registration failed - no redirect")
        # Print any error messages
        try:
            messages = list(get_messages(response.wsgi_request))
            for message in messages:
                print(f"Message: {message}")
        except:
            pass
        return False

def test_email_functionality():
    """Test email functionality"""
    print("\n--- Testing Email Functionality ---")
    
    from django.conf import settings
    from django.core.mail import send_mail
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    try:
        # Test sending email
        result = send_mail(
            'Test Email Subject',
            'This is a test email message.',
            settings.EMAIL_HOST_USER,
            ['test@example.com'],
            fail_silently=False,
        )
        print(f"✓ Email sent successfully: {result}")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

def main():
    """Run all tests"""
    results = []
    
    results.append(("Simple Registration", test_simple_registration()))
    results.append(("View Registration", test_view_registration()))
    results.append(("Email Functionality", test_email_functionality()))
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

if __name__ == '__main__':
    main()