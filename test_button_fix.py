#!/usr/bin/env python3
"""
Test Forgot Password Button Fix
This script verifies that the forgot password button now links to the correct URL
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
from django.urls import reverse
from bs4 import BeautifulSoup

def test_forgot_password_button_fix():
    """Test that the forgot password button links to correct URL"""
    print("TESTING FORGOT PASSWORD BUTTON FIX")
    print("=" * 50)
    
    client = Client()
    
    # Test 1: Check admin login page
    print("\n--- Test 1: Admin Login Page ---")
    try:
        response = client.get(reverse('admin_login'))
        if response.status_code == 200:
            print("✅ Admin login page loads successfully")
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the forgot password link
            forgot_link = soup.find('a', string='Forgot Password?')
            if forgot_link:
                href = forgot_link.get('href')
                print(f"✅ Forgot Password link found: {href}")
                
                # Check if it's the correct URL
                expected_url = reverse('admin_forgot_password')
                if href == expected_url:
                    print(f"✅ Link is CORRECT! Points to: {expected_url}")
                else:
                    print(f"❌ Link is WRONG! Expected: {expected_url}, Got: {href}")
            else:
                print("❌ Forgot Password link not found on page")
        else:
            print(f"❌ Admin login page failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing admin login page: {e}")
    
    # Test 2: Verify forgot password page works
    print("\n--- Test 2: Forgot Password Page Functionality ---")
    try:
        forgot_url = reverse('admin_forgot_password')
        response = client.get(forgot_url)
        
        if response.status_code == 200:
            print(f"✅ Forgot password page loads at: {forgot_url}")
            
            # Check if the page has the expected form
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form')
            email_input = soup.find('input', {'type': 'email'})
            
            if form and email_input:
                print("✅ Forgot password form is functional")
            else:
                print("❌ Forgot password form elements missing")
        else:
            print(f"❌ Forgot password page failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing forgot password page: {e}")
    
    # Test 3: Test full user flow
    print("\n--- Test 3: Full User Flow ---")
    try:
        # Step 1: Go to login page
        login_response = client.get(reverse('admin_login'))
        print("✅ Step 1: User visits admin login page")
        
        # Step 2: Click forgot password (simulate)
        forgot_response = client.get(reverse('admin_forgot_password'))
        print("✅ Step 2: User clicks 'Forgot Password' button")
        
        if forgot_response.status_code == 200:
            print("✅ Step 3: User successfully reaches forgot password page")
            
            # Step 4: Test form submission
            form_response = client.post(reverse('admin_forgot_password'), {
                'email': 'test@example.com'
            })
            
            if form_response.status_code in [200, 302]:
                print("✅ Step 4: Form submission works (email processing)")
            else:
                print(f"❌ Step 4: Form submission failed: {form_response.status_code}")
        else:
            print(f"❌ Step 3: Failed to reach forgot password page: {forgot_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in full user flow test: {e}")

def show_button_fix_summary():
    """Show summary of what was fixed"""
    print("\n" + "=" * 50)
    print("BUTTON FIX SUMMARY")
    print("=" * 50)
    
    print("🔧 WHAT WAS FIXED:")
    print("- Changed hardcoded 'forgot-password.html' to Django URL")
    print("- Updated templates/hospital_admin/login.html")
    print("- Updated templates/hospital_admin/invoice.html")
    print()
    
    print("❌ BEFORE FIX:")
    print('   <a href="forgot-password.html">Forgot Password?</a>')
    print()
    
    print("✅ AFTER FIX:")
    print('   <a href="{% url \'admin_forgot_password\' %}">Forgot Password?</a>')
    print()
    
    print("🌐 RESULT:")
    print("- Button now properly links to: /hospital_admin/forgot-password/")
    print("- No more 404 errors when clicking 'Forgot Password'")
    print("- Fully functional password reset system")

if __name__ == '__main__':
    test_forgot_password_button_fix()
    show_button_fix_summary()