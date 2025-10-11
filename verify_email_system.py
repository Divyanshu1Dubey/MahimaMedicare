#!/usr/bin/env python
"""
Comprehensive Email System Verification Script
Tests all email functionality and configurations
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')

import django
django.setup()

from healthstack.email_utils import send_email_safely, send_doctor_acceptance_email
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def test_basic_email():
    """Test basic email sending functionality."""
    print("🔧 Testing Basic Email Configuration...")
    
    result = send_email_safely(
        subject="Mahima Medicare - Email System Test",
        message="This is a test email from Mahima Medicare system to verify the email configuration is working properly.",
        from_email="mahimamedicare.web@gmail.com",
        recipient_list=["mahimamedicare.web@gmail.com"],
        fail_silently=True
    )
    
    if result:
        print("✅ Basic email test PASSED")
        return True
    else:
        print("❌ Basic email test FAILED")
        return False

def test_doctor_acceptance_email():
    """Test doctor acceptance email template and functionality."""
    print("\n🩺 Testing Doctor Acceptance Email...")
    
    result = send_doctor_acceptance_email(
        doctor_name="Dr. Test Kumar",
        doctor_email="mahimamedicare.web@gmail.com",
        doctor_department="Cardiology",
        doctor_specialization="Heart Surgery"
    )
    
    if result:
        print("✅ Doctor acceptance email test PASSED")
        return True
    else:
        print("❌ Doctor acceptance email test FAILED")
        return False

def test_html_email_template():
    """Test HTML email template rendering."""
    print("\n📧 Testing HTML Email Template...")
    
    try:
        values = {
            "doctor_name": "Dr. Test Kumar",
            "doctor_email": "mahimamedicare.web@gmail.com",
            "doctor_department": "Cardiology",
            "doctor_specialization": "Heart Surgery",
        }
        
        html_message = render_to_string('hospital_admin/accept-doctor-mail.html', {'values': values})
        plain_message = strip_tags(html_message)
        
        if html_message and plain_message:
            print("✅ HTML template rendering PASSED")
            return True
        else:
            print("❌ HTML template rendering FAILED - Empty content")
            return False
            
    except Exception as e:
        print(f"❌ HTML template rendering FAILED - {str(e)}")
        return False

def test_django_send_mail():
    """Test Django's built-in send_mail function."""
    print("\n📬 Testing Django send_mail Function...")
    
    try:
        result = send_mail(
            subject="Mahima Medicare - Django Send Mail Test",
            message="This is a test using Django's built-in send_mail function.",
            from_email="mahimamedicare.web@gmail.com",
            recipient_list=["mahimamedicare.web@gmail.com"],
            fail_silently=False
        )
        
        if result > 0:
            print("✅ Django send_mail test PASSED")
            return True
        else:
            print("❌ Django send_mail test FAILED - No emails sent")
            return False
            
    except Exception as e:
        print(f"❌ Django send_mail test FAILED - {str(e)}")
        return False

def test_email_configuration():
    """Test email configuration settings."""
    print("\n⚙️ Testing Email Configuration...")
    
    from django.conf import settings
    
    print(f"   📍 EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not Set')}")
    print(f"   📍 EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not Set')}")
    print(f"   📍 EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not Set')}")
    print(f"   📍 EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not Set')}")
    print(f"   📍 EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not Set')}")
    print(f"   📍 DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not Set')}")
    
    # Check if all required settings are present
    required_settings = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
    missing_settings = []
    
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"❌ Missing email settings: {', '.join(missing_settings)}")
        return False
    else:
        print("✅ All email configuration settings are present")
        return True

def main():
    print("🏥 MAHIMA MEDICARE - EMAIL SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_email_configuration,
        test_basic_email,
        test_html_email_template,
        test_doctor_acceptance_email,
        test_django_send_mail,
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL EMAIL TESTS PASSED! Email system is fully functional.")
        print("\n📋 Email System Status:")
        print("   ✅ SMTP Authentication: Working")
        print("   ✅ Email Templates: Working")
        print("   ✅ Doctor Notifications: Working")
        print("   ✅ System Integration: Complete")
        print("\n💡 Your email alerts and notifications are now fully operational!")
        return True
    else:
        print("⚠️  Some email tests failed. Check the errors above.")
        print("\n🔍 Troubleshooting Steps:")
        print("   1. Verify Gmail App Password is correct")
        print("   2. Check internet connectivity")
        print("   3. Ensure Gmail account has 2FA enabled")
        print("   4. Check Django settings configuration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)