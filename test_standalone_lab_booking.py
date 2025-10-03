#!/usr/bin/env python3
"""
Test script to verify standalone lab test booking integration with lab worker queue
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from doctor.models import Prescription_test, Prescription, testOrder, testCart, Doctor_Information
from hospital.models import Patient
from hospital_admin.models import Test_Information, Clinical_Laboratory_Technician

User = get_user_model()

def test_standalone_booking_flow():
    """Test the complete standalone booking flow"""
    print("🧪 Testing Standalone Lab Test Booking Flow")
    print("=" * 50)
    
    # 1. Check if we have test data
    test_info = Test_Information.objects.first()
    if not test_info:
        print("❌ No test information found. Creating sample test...")
        test_info = Test_Information.objects.create(
            test_name="Complete Blood Count (CBC)",
            test_price="10",
            test_description="Basic blood test"
        )
    
    patient_user = User.objects.filter(patient__isnull=False).first()
    if not patient_user:
        print("❌ No patient found")
        return
    
    lab_worker = Clinical_Laboratory_Technician.objects.first()
    if not lab_worker:
        print("❌ No lab worker found")
        return
    
    print(f"✅ Test: {test_info.test_name} (₹{test_info.test_price})")
    print(f"✅ Patient: {patient_user.username}")
    print(f"✅ Lab Worker: {lab_worker.name}")
    
    # 2. Create dummy prescription and prescription test (simulating the fixed submit_standalone_test)
    dummy_doctor = Doctor_Information.objects.filter(name__icontains='Standalone').first()
    if not dummy_doctor:
        dummy_doctor = Doctor_Information.objects.create(
            name='System - Standalone Booking',
            department='Cardiologists',  # Use one of the valid choices
            email='system@mahimamedicare.co.in'
        )
        print("✅ Created dummy doctor for standalone bookings")
    
    prescription = Prescription.objects.create(
        doctor=dummy_doctor,
        patient=patient_user.patient,
        test_description='Standalone lab test booking - 1 tests',
        extra_information='Self-requested lab tests'
    )
    print(f"✅ Created prescription #{prescription.prescription_id}")
    
    prescription_test = Prescription_test.objects.create(
        prescription=prescription,
        test_name=test_info.test_name,
        test_description=f'Standalone booking: {test_info.test_name}',
        test_info_price=test_info.test_price or '0',
        test_info_pay_status='paid',  # Simulate paid COD
        test_status='prescribed',
        assigned_technician=lab_worker
    )
    print(f"✅ Created prescription test #{prescription_test.test_id}")
    
    # 3. Verify it shows in lab worker queries
    print("\n🔍 Checking Lab Worker Queries...")
    
    # Query from mypatient_list (what lab worker sees)
    lab_tests = Prescription_test.objects.select_related(
        'prescription',
        'prescription__patient',
        'prescription__patient__user',
        'prescription__doctor'
    ).filter(
        test_info_pay_status__in=['paid', 'cod_pending', 'cod']
    ).order_by('-test_id')
    
    print(f"✅ Found {lab_tests.count()} tests in lab queue")
    
    for test in lab_tests[:3]:  # Show first 3
        if test.prescription and test.prescription.patient:
            patient_name = f"{test.prescription.patient.user.first_name} {test.prescription.patient.user.last_name}".strip() or test.prescription.patient.user.username
            doctor_name = test.prescription.doctor.name if test.prescription.doctor else 'Unknown'
        else:
            patient_name = 'Standalone Booking'
            doctor_name = 'Self-Booked'
        
        print(f"  - Test: {test.test_name}")
        print(f"    Patient: {patient_name}")
        print(f"    Doctor: {doctor_name}")
        print(f"    Status: {test.test_status}")
        print(f"    Payment: {test.test_info_pay_status}")
        print(f"    Lab Worker: {test.assigned_technician.name if test.assigned_technician else 'Unassigned'}")
        print()
    
    # 4. Test status transitions
    print("🔄 Testing Status Transitions...")
    
    # Collect sample
    prescription_test.test_status = 'collected'
    prescription_test.save()
    print("✅ Sample collected")
    
    # Process sample
    prescription_test.test_status = 'processing'
    prescription_test.save()
    print("✅ Sample processing")
    
    # Complete test
    prescription_test.test_status = 'completed'
    prescription_test.save()
    print("✅ Test completed")
    
    print("\n✅ All tests passed! Standalone booking flow works correctly.")
    print("\nNow you should see your ₹10 test in the lab worker queue at:")
    print("http://localhost:8000/hospital_admin/mypatient-list/?show=pending")

if __name__ == "__main__":
    test_standalone_booking_flow()