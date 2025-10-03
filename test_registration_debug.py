#!/usr/bin/env python3
"""
Test Lab Technician Registration Debug
This script identifies and fixes issues with lab technician registration and email functionality
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

from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.exceptions import ValidationError
from django.db import transaction
from hospital.models import User
from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician
from hospital_admin.forms import LabWorkerCreationForm
import traceback

class RegistrationDebugTest(TransactionTestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            is_hospital_admin=True
        )
        
        # Create admin information
        self.admin_info = Admin_Information.objects.create(
            user=self.admin_user,
            username='admin_test',
            name='Test Admin',
            email='admin@test.com'
        )
        
        print(f"✓ Setup completed - Admin user created: {self.admin_user.username}")

    def test_1_form_validation(self):
        """Test 1: Form validation"""
        print("\n=== TEST 1: Form Validation ===")
        
        # Test valid data
        valid_data = {
            'username': 'lab_tech_1',
            'email': 'labtech1@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        form = LabWorkerCreationForm(data=valid_data)
        print(f"Form with valid data - Valid: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        else:
            print("✓ Form validation passed")
        
        # Test invalid data (mismatched passwords)
        invalid_data = {
            'username': 'lab_tech_2',
            'email': 'labtech2@test.com',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        
        form = LabWorkerCreationForm(data=invalid_data)
        print(f"Form with invalid data - Valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Expected form errors: {form.errors}")
        
        return True

    def test_2_registration_process(self):
        """Test 2: Registration process step by step"""
        print("\n=== TEST 2: Registration Process ===")
        
        # Login as admin
        self.client.login(username='admin_test', password='testpass123')
        print("✓ Admin logged in")
        
        # Test GET request to registration page
        response = self.client.get(reverse('add-lab-worker'))
        print(f"GET request status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Registration page loads successfully")
        else:
            print(f"✗ Registration page failed to load: {response.status_code}")
            return False
        
        # Test POST request with valid data
        lab_data = {
            'username': 'lab_technician_test',
            'email': 'labtech@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        print(f"Attempting to create lab technician with data: {lab_data}")
        
        # Check users before creation
        users_before = User.objects.count()
        lab_techs_before = Clinical_Laboratory_Technician.objects.count()
        print(f"Users before: {users_before}, Lab techs before: {lab_techs_before}")
        
        response = self.client.post(reverse('add-lab-worker'), data=lab_data)
        
        # Check users after creation
        users_after = User.objects.count()
        lab_techs_after = Clinical_Laboratory_Technician.objects.count()
        print(f"Users after: {users_after}, Lab techs after: {lab_techs_after}")
        
        print(f"POST request status: {response.status_code}")
        
        # Check if user was created
        try:
            created_user = User.objects.get(username='lab_technician_test')
            print(f"✓ User created: {created_user.username}")
            print(f"User is_labworker: {created_user.is_labworker}")
            
            # Check if Clinical_Laboratory_Technician was created
            try:
                lab_tech = Clinical_Laboratory_Technician.objects.get(user=created_user)
                print(f"✓ Lab technician profile created: {lab_tech}")
                return True
            except Clinical_Laboratory_Technician.DoesNotExist:
                print("✗ Lab technician profile NOT created - This is the bug!")
                return False
                
        except User.DoesNotExist:
            print("✗ User was NOT created")
            
            # Check for messages
            messages = list(get_messages(response.wsgi_request))
            for message in messages:
                print(f"Message: {message}")
            
            return False

    def test_3_form_error_debugging(self):
        """Test 3: Debug form errors in detail"""
        print("\n=== TEST 3: Form Error Debugging ===")
        
        self.client.login(username='admin_test', password='testpass123')
        
        # Test with various problematic data
        test_cases = [
            {
                'name': 'Empty username',
                'data': {'username': '', 'email': 'test@test.com', 'password1': 'test123', 'password2': 'test123'}
            },
            {
                'name': 'Short password',
                'data': {'username': 'test', 'email': 'test@test.com', 'password1': '123', 'password2': '123'}
            },
            {
                'name': 'Invalid email',
                'data': {'username': 'test', 'email': 'invalid-email', 'password1': 'test123', 'password2': 'test123'}
            },
            {
                'name': 'Duplicate username',
                'data': {'username': 'admin_test', 'email': 'new@test.com', 'password1': 'test123', 'password2': 'test123'}
            }
        ]
        
        for case in test_cases:
            print(f"\nTesting: {case['name']}")
            form = LabWorkerCreationForm(data=case['data'])
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
            else:
                print("Form is valid (unexpected)")
        
        return True

    def test_4_signal_debugging(self):
        """Test 4: Debug signal handling"""
        print("\n=== TEST 4: Signal Debugging ===")
        
        # Create user manually and check if signal fires
        print("Creating user manually to test signals...")
        
        with transaction.atomic():
            user = User.objects.create_user(
                username='manual_lab_tech',
                email='manual@test.com',
                password='testpass123'
            )
            user.is_labworker = True
            user.save()
            print(f"✓ User created: {user.username}, is_labworker: {user.is_labworker}")
            
            # Check if Clinical_Laboratory_Technician was created by signal
            try:
                lab_tech = Clinical_Laboratory_Technician.objects.get(user=user)
                print(f"✓ Signal worked - Lab technician created: {lab_tech}")
                return True
            except Clinical_Laboratory_Technician.DoesNotExist:
                print("✗ Signal failed - No lab technician profile created")
                return False

def test_forgot_password_functionality():
    """Test forgot password functionality"""
    print("\n=== TESTING FORGOT PASSWORD FUNCTIONALITY ===")
    
    client = Client()
    
    # Test if forgot password page exists
    try:
        response = client.get(reverse('admin_forgot_password'))
        print(f"Forgot password page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Forgot password page loads")
        else:
            print("✗ Forgot password page doesn't load")
            
    except Exception as e:
        print(f"✗ Error accessing forgot password page: {e}")
    
    # Test email configuration
    print("\nTesting email configuration...")
    from django.conf import settings
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not configured')}")
    
    # Test sending a simple email
    try:
        from django.core.mail import send_mail
        
        result = send_mail(
            'Test Email',
            'This is a test email.',
            settings.EMAIL_HOST_USER,
            ['test@example.com'],
            fail_silently=False,
        )
        print(f"✓ Test email sent successfully: {result}")
        
    except Exception as e:
        print(f"✗ Email sending failed: {e}")

def main():
    """Main test execution"""
    print("MAHIMA MEDICARE - REGISTRATION & EMAIL DEBUG")
    print("=" * 50)
    
    # Run registration tests
    test = RegistrationDebugTest()
    test.setUp()
    
    results = []
    
    try:
        results.append(("Form Validation", test.test_1_form_validation()))
        results.append(("Registration Process", test.test_2_registration_process()))
        results.append(("Form Error Debugging", test.test_3_form_error_debugging()))
        results.append(("Signal Debugging", test.test_4_signal_debugging()))
    except Exception as e:
        print(f"Test error: {e}")
        traceback.print_exc()
    
    # Test forgot password functionality
    test_forgot_password_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print("\nDEBUG COMPLETE")

if __name__ == '__main__':
    main()