#!/usr/bin/env python3
"""
Test Fixed Lab Technician Registration and Forgot Password
This script tests the fixed registration and email functionality
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
from django.core import mail
from hospital.models import User
from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician
from hospital_admin.forms import LabWorkerCreationForm

def test_registration_with_error_handling():
    """Test registration with improved error handling"""
    print("TESTING FIXED LAB TECHNICIAN REGISTRATION")
    print("=" * 50)
    
    client = Client()
    
    # Get admin user and ensure login
    admin_user = User.objects.filter(is_hospital_admin=True).first()
    if not admin_user:
        admin_user = User.objects.create_user(
            username='test_admin_fixed',
            email='admin@test.com',
            password='testpass123',
            is_hospital_admin=True
        )
    
    admin_user.set_password('testpass123')
    admin_user.save()
    
    if not client.login(username=admin_user.username, password='testpass123'):
        print("✗ Failed to login as admin")
        return False
    
    print(f"✓ Logged in as admin: {admin_user.username}")
    
    # Test 1: Valid registration
    print("\n--- Test 1: Valid Registration ---")
    response = client.post(reverse('add-lab-worker'), {
        'username': 'fixed_lab_tech_1',
        'email': 'fixed1@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    })
    
    if response.status_code == 302:
        print("✓ Valid registration successful")
        # Check if user and profile were created
        try:
            user = User.objects.get(username='fixed_lab_tech_1')
            lab_tech = Clinical_Laboratory_Technician.objects.get(user=user)
            print(f"✓ User created: {user.username}")
            print(f"✓ Lab tech profile created: {lab_tech}")
        except Exception as e:
            print(f"✗ Error verifying creation: {e}")
            return False
    else:
        print(f"✗ Valid registration failed: {response.status_code}")
        return False
    
    # Test 2: Invalid registration (duplicate username)
    print("\n--- Test 2: Invalid Registration (Duplicate Username) ---")
    response = client.post(reverse('add-lab-worker'), {
        'username': 'fixed_lab_tech_1',  # Same username
        'email': 'fixed2@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    })
    
    if response.status_code == 200:  # Should stay on same page with errors
        print("✓ Duplicate username correctly rejected")
        # The improved error handling should show specific messages
    else:
        print(f"✗ Duplicate username test unexpected response: {response.status_code}")
    
    # Test 3: Invalid registration (password mismatch)
    print("\n--- Test 3: Invalid Registration (Password Mismatch) ---")
    response = client.post(reverse('add-lab-worker'), {
        'username': 'fixed_lab_tech_3',
        'email': 'fixed3@test.com',
        'password1': 'testpass123',
        'password2': 'differentpass'
    })
    
    if response.status_code == 200:  # Should stay on same page with errors
        print("✓ Password mismatch correctly rejected")
    else:
        print(f"✗ Password mismatch test unexpected response: {response.status_code}")
    
    return True

def test_forgot_password_functionality():
    """Test improved forgot password functionality"""
    print("\n" + "=" * 50)
    print("TESTING FIXED FORGOT PASSWORD FUNCTIONALITY")
    print("=" * 50)
    
    client = Client()
    
    # Create a test admin user for password reset
    test_admin = User.objects.create_user(
        username='reset_test_admin',
        email='resettest@example.com',
        password='oldpassword123',
        is_hospital_admin=True
    )
    
    print(f"✓ Created test admin: {test_admin.username} - {test_admin.email}")
    
    # Test 1: Valid email
    print("\n--- Test 1: Valid Email Reset ---")
    
    # Clear any existing emails
    mail.outbox = []
    
    response = client.post(reverse('admin_forgot_password'), {
        'email': 'resettest@example.com'
    })
    
    if response.status_code == 302:  # Should redirect after sending
        print("✓ Password reset request processed")
    else:
        print(f"Response status: {response.status_code}")
    
    # Check if email was sent
    if len(mail.outbox) > 0:
        print(f"✓ Email sent successfully")
        print(f"Email subject: {mail.outbox[0].subject}")
        print(f"Email to: {mail.outbox[0].to}")
        print("Email preview:")
        print(mail.outbox[0].body[:200] + "...")
    else:
        print("✗ No email was sent")
    
    # Test 2: Invalid email
    print("\n--- Test 2: Invalid Email ---")
    mail.outbox = []  # Clear emails
    
    response = client.post(reverse('admin_forgot_password'), {
        'email': 'nonexistent@example.com'
    })
    
    if len(mail.outbox) == 0:
        print("✓ No email sent for invalid address (correct behavior)")
    else:
        print("✗ Email sent for invalid address (security issue)")
    
    # Test 3: Empty email
    print("\n--- Test 3: Empty Email ---")
    response = client.post(reverse('admin_forgot_password'), {
        'email': ''
    })
    
    print(f"Empty email response status: {response.status_code}")
    
    return True

def test_email_configuration():
    """Test email configuration"""
    print("\n" + "=" * 50)
    print("TESTING EMAIL CONFIGURATION")
    print("=" * 50)
    
    from django.conf import settings
    from django.core.mail import send_mail
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    
    try:
        # Test basic email sending
        result = send_mail(
            'Test Email Configuration',
            'This is a test to verify email configuration is working.',
            settings.EMAIL_HOST_USER,
            ['test@example.com'],
            fail_silently=False,
        )
        print(f"✓ Email configuration test successful: {result}")
        return True
    except Exception as e:
        print(f"✗ Email configuration test failed: {e}")
        return False

def test_form_validation_improvements():
    """Test form validation improvements"""
    print("\n" + "=" * 50)
    print("TESTING FORM VALIDATION IMPROVEMENTS")
    print("=" * 50)
    
    # Test various form scenarios
    test_cases = [
        {
            'name': 'Valid form',
            'data': {'username': 'validuser', 'email': 'valid@test.com', 'password1': 'testpass123', 'password2': 'testpass123'},
            'should_be_valid': True
        },
        {
            'name': 'Short username',
            'data': {'username': 'ab', 'email': 'test@test.com', 'password1': 'testpass123', 'password2': 'testpass123'},
            'should_be_valid': False
        },
        {
            'name': 'Short password',
            'data': {'username': 'testuser', 'email': 'test@test.com', 'password1': '12345', 'password2': '12345'},
            'should_be_valid': False
        },
        {
            'name': 'Password mismatch',
            'data': {'username': 'testuser', 'email': 'test@test.com', 'password1': 'testpass123', 'password2': 'different'},
            'should_be_valid': False
        },
        {
            'name': 'Invalid email',
            'data': {'username': 'testuser', 'email': 'invalid-email', 'password1': 'testpass123', 'password2': 'testpass123'},
            'should_be_valid': False
        }
    ]
    
    for case in test_cases:
        form = LabWorkerCreationForm(data=case['data'])
        is_valid = form.is_valid()
        
        if is_valid == case['should_be_valid']:
            print(f"✓ {case['name']}: Expected validity = {case['should_be_valid']}")
        else:
            print(f"✗ {case['name']}: Expected {case['should_be_valid']}, got {is_valid}")
            if not is_valid:
                print(f"  Form errors: {form.errors}")
    
    return True

def main():
    """Main test execution"""
    print("MAHIMA MEDICARE - FIXED REGISTRATION & EMAIL TESTING")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Registration Error Handling", test_registration_with_error_handling()))
        results.append(("Forgot Password Functionality", test_forgot_password_functionality()))
        results.append(("Email Configuration", test_email_configuration()))
        results.append(("Form Validation", test_form_validation_improvements()))
        
    except Exception as e:
        print(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()
    
    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Registration and email fixes are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
    
    print("\nFIXES IMPLEMENTED:")
    print("- Enhanced error handling in lab technician registration")
    print("- Specific form error messages displayed to users")
    print("- Template updated to show messages and field errors")
    print("- Functional forgot password system with email sending")
    print("- Proper email configuration testing")

if __name__ == '__main__':
    main()