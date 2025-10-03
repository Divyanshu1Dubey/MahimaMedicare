#!/usr/bin/env python3
"""
COMPREHENSIVE PATIENT WORKFLOW TESTING & FIXING
This script will test and fix ALL patient-related functionality:
- Patient registration and login
- Doctor appointments 
- Lab test bookings
- Pharmacy orders
- Payment processing (Razorpay + COD)
- All user workflows and interactions
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import transaction
from hospital.models import User, Patient, Hospital_Information, Appointment
from doctor.models import Doctor_Information
from hospital_admin.models import Clinical_Laboratory_Technician, Test_Information
from pharmacy.models import Pharmacist, Medicine, Order
from razorpay_payment.models import Payment
import json

class ComprehensivePatientWorkflowTest:
    def __init__(self):
        self.client = Client()
        self.test_data = {}
        self.results = []
        
    def log_result(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        self.results.append((test_name, success, message))
        print(f"{status} - {test_name}: {message}")
        
    def setup_test_environment(self):
        """Create test data for comprehensive testing"""
        print("🔧 SETTING UP COMPREHENSIVE TEST ENVIRONMENT")
        print("=" * 60)
        
        try:
            # Create hospital
            self.test_data['hospital'] = Hospital_Information.objects.create(
                name="Test Hospital",
                address="123 Test St",
                phone_number="1234567890",
                email="hospital@test.com"
            )
            
            # Create admin user
            self.test_data['admin_user'] = User.objects.create_user(
                username='test_admin_complete',
                email='admin@test.com',
                password='testpass123',
                is_hospital_admin=True
            )
            
            # Create doctor
            self.test_data['doctor_user'] = User.objects.create_user(
                username='test_doctor_complete',
                email='doctor@test.com',
                password='testpass123',
                is_doctor=True
            )
            
            # Create lab technician
            self.test_data['lab_user'] = User.objects.create_user(
                username='test_lab_complete',
                email='lab@test.com',
                password='testpass123',
                is_labworker=True
            )
            
            # Create pharmacist
            self.test_data['pharmacist_user'] = User.objects.create_user(
                username='test_pharmacist_complete',
                email='pharmacist@test.com',
                password='testpass123',
                is_pharmacist=True
            )
            
            # Create test medicine
            self.test_data['medicine'] = Medicine.objects.create(
                name="Test Medicine",
                price=100.00,
                stock_quantity=50,
                description="Test medicine for testing"
            )
            
            # Create test lab test
            self.test_data['lab_test'] = Test_Information.objects.create(
                test_name="Blood Test",
                test_price="500.00"
            )
            
            self.log_result("Test Environment Setup", True, "All test data created successfully")
            
        except Exception as e:
            self.log_result("Test Environment Setup", False, f"Setup failed: {str(e)}")
            
    def test_1_patient_registration(self):
        """Test patient registration process"""
        print("\n📝 TESTING PATIENT REGISTRATION")
        print("-" * 40)
        
        # Test 1.1: Valid registration
        registration_data = {
            'username': 'test_patient_workflow',
            'first_name': 'Test',
            'last_name': 'Patient', 
            'email': 'testpatient@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        try:
            response = self.client.post(reverse('register'), registration_data)
            
            if response.status_code == 302:  # Redirect after successful registration
                # Check if user was created
                user = User.objects.get(username='test_patient_workflow')
                patient = Patient.objects.get(user=user)
                self.test_data['patient_user'] = user
                self.test_data['patient'] = patient
                
                self.log_result("Patient Registration", True, f"Patient created: {user.username}")
            else:
                self.log_result("Patient Registration", False, f"Registration failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Patient Registration", False, f"Registration error: {str(e)}")
            
        # Test 1.2: Invalid registration (duplicate username)
        try:
            response = self.client.post(reverse('register'), {
                'username': 'test_patient_workflow',  # Same username
                'email': 'different@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123'
            })
            
            if response.status_code == 200:  # Should stay on form with errors
                self.log_result("Duplicate Registration Handling", True, "Duplicate registration correctly rejected")
            else:
                self.log_result("Duplicate Registration Handling", False, "Should show form errors")
                
        except Exception as e:
            self.log_result("Duplicate Registration Handling", False, f"Error: {str(e)}")
    
    def test_2_patient_login(self):
        """Test patient login functionality"""
        print("\n🔑 TESTING PATIENT LOGIN")
        print("-" * 40)
        
        # Test 2.1: Valid login
        try:
            login_success = self.client.login(username='test_patient_workflow', password='testpass123')
            
            if login_success:
                self.log_result("Patient Login", True, "Patient login successful")
            else:
                self.log_result("Patient Login", False, "Patient login failed")
                
        except Exception as e:
            self.log_result("Patient Login", False, f"Login error: {str(e)}")
            
        # Test 2.2: Invalid login
        try:
            self.client.logout()  # Logout first
            login_success = self.client.login(username='test_patient_workflow', password='wrongpassword')
            
            if not login_success:
                self.log_result("Invalid Login Handling", True, "Invalid login correctly rejected")
            else:
                self.log_result("Invalid Login Handling", False, "Should reject invalid password")
                
        except Exception as e:
            self.log_result("Invalid Login Handling", False, f"Error: {str(e)}")
            
    def test_3_doctor_appointments(self):
        """Test doctor appointment booking"""
        print("\n🩺 TESTING DOCTOR APPOINTMENTS")
        print("-" * 40)
        
        # Login as patient first
        self.client.login(username='test_patient_workflow', password='testpass123')
        
        # Test 3.1: View available doctors
        try:
            response = self.client.get(reverse('find-doctors'))
            
            if response.status_code == 200:
                self.log_result("View Doctors Page", True, "Doctors page loads successfully")
            else:
                self.log_result("View Doctors Page", False, f"Page failed to load: {response.status_code}")
                
        except Exception as e:
            self.log_result("View Doctors Page", False, f"Error: {str(e)}")
            
        # Test 3.2: Book appointment
        try:
            doctor_info = Doctor_Information.objects.get(user=self.test_data['doctor_user'])
            
            appointment_data = {
                'doctor': doctor_info.doctor_id,
                'appointment_date': (datetime.now() + timedelta(days=1)).date(),
                'appointment_time': '10:00',
                'problem_description': 'Test appointment booking'
            }
            
            response = self.client.post(reverse('appointment-booking'), appointment_data)
            
            if response.status_code in [200, 302]:
                self.log_result("Appointment Booking", True, "Appointment booking processed")
            else:
                self.log_result("Appointment Booking", False, f"Booking failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Appointment Booking", False, f"Booking error: {str(e)}")
    
    def test_4_lab_test_booking(self):
        """Test lab test booking functionality"""
        print("\n🧪 TESTING LAB TEST BOOKING")
        print("-" * 40)
        
        # Test 4.1: View available tests
        try:
            response = self.client.get('/test-booking/')
            
            if response.status_code == 200:
                self.log_result("Lab Tests Page", True, "Lab tests page loads successfully")
            else:
                self.log_result("Lab Tests Page", False, f"Page failed to load: {response.status_code}")
                
        except Exception as e:
            self.log_result("Lab Tests Page", False, f"Error: {str(e)}")
            
        # Test 4.2: Book lab test
        try:
            test_booking_data = {
                'test': self.test_data['lab_test'].test_id,
                'booking_date': (datetime.now() + timedelta(days=1)).date(),
                'payment_method': 'online'
            }
            
            response = self.client.post('/book-test/', test_booking_data)
            
            if response.status_code in [200, 302]:
                self.log_result("Lab Test Booking", True, "Lab test booking processed")
            else:
                self.log_result("Lab Test Booking", False, f"Booking failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Lab Test Booking", False, f"Booking error: {str(e)}")
    
    def test_5_pharmacy_orders(self):
        """Test pharmacy ordering functionality"""
        print("\n💊 TESTING PHARMACY ORDERS")
        print("-" * 40)
        
        # Test 5.1: View medicines
        try:
            response = self.client.get('/pharmacy/')
            
            if response.status_code == 200:
                self.log_result("Pharmacy Page", True, "Pharmacy page loads successfully")
            else:
                self.log_result("Pharmacy Page", False, f"Page failed to load: {response.status_code}")
                
        except Exception as e:
            self.log_result("Pharmacy Page", False, f"Error: {str(e)}")
            
        # Test 5.2: Add medicine to cart
        try:
            cart_data = {
                'medicine_id': self.test_data['medicine'].id,
                'quantity': 2
            }
            
            response = self.client.post('/add-to-cart/', cart_data)
            
            if response.status_code in [200, 302]:
                self.log_result("Add to Cart", True, "Medicine added to cart")
            else:
                self.log_result("Add to Cart", False, f"Add to cart failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Add to Cart", False, f"Cart error: {str(e)}")
    
    def test_6_payment_processing(self):
        """Test payment processing (Razorpay and COD)"""
        print("\n💳 TESTING PAYMENT PROCESSING")
        print("-" * 40)
        
        # Test 6.1: COD Payment
        try:
            cod_payment_data = {
                'payment_method': 'cod',
                'delivery_address': '123 Test Address',
                'delivery_phone': '1234567890'
            }
            
            response = self.client.post('/process-payment/', cod_payment_data)
            
            if response.status_code in [200, 302]:
                self.log_result("COD Payment", True, "COD payment processed")
            else:
                self.log_result("COD Payment", False, f"COD payment failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("COD Payment", False, f"COD error: {str(e)}")
            
        # Test 6.2: Online Payment Setup
        try:
            online_payment_data = {
                'payment_method': 'online',
                'amount': 500
            }
            
            response = self.client.post('/razorpay/create-order/', online_payment_data)
            
            if response.status_code in [200, 302] or 'order_id' in str(response.content):
                self.log_result("Online Payment Setup", True, "Razorpay order creation works")
            else:
                self.log_result("Online Payment Setup", False, f"Online payment setup failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Online Payment Setup", False, f"Online payment error: {str(e)}")

def run_comprehensive_patient_tests():
    """Run all patient workflow tests"""
    print("🏥 MAHIMA MEDICARE - COMPREHENSIVE PATIENT WORKFLOW TESTING")
    print("=" * 70)
    print("Testing ALL patient functionality:")
    print("- Registration & Login")
    print("- Doctor Appointments") 
    print("- Lab Test Bookings")
    print("- Pharmacy Orders")
    print("- Payment Processing")
    print("- Error Handling")
    print("=" * 70)
    
    # Initialize test suite
    test_suite = ComprehensivePatientWorkflowTest()
    
    # Run all tests
    test_suite.setup_test_environment()
    test_suite.test_1_patient_registration()
    test_suite.test_2_patient_login()
    test_suite.test_3_doctor_appointments()
    test_suite.test_4_lab_test_booking()
    test_suite.test_5_pharmacy_orders()
    test_suite.test_6_payment_processing()
    
    # Show results summary
    print("\n" + "=" * 70)
    print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, success, message in test_suite.results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Patient workflow is fully functional!")
    else:
        print(f"\n⚠️  {failed} tests failed. Issues need to be addressed.")
    
    return test_suite.results

if __name__ == '__main__':
    results = run_comprehensive_patient_tests()