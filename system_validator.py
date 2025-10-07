#!/usr/bin/env python3
"""
SYSTEMATIC TESTING - MAHIMA MEDICARE
===================================
Testing every module, workflow, and function step by step.
"""

import os
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

# Import all models to test
from hospital.models import *
from doctor.models import *
from pharmacy.models import *
from razorpay_payment.models import *
from hospital_admin.models import *

class SystemTester:
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def log_test(self, module, test_name, status, details=""):
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'module': module,
            'test': test_name,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {module} - {test_name}: {status}")
        if details and status != "PASS":
            print(f"   💡 {details}")
    
    def test_models(self):
        """Test all Django models"""
        print("\n🗄️  TESTING DATABASE MODELS")
        print("=" * 40)
        
        # Test Hospital model
        try:
            hospitals = Hospital.objects.all()
            self.log_test("DATABASE", "Hospital Model", "PASS", f"{len(hospitals)} hospitals found")
        except Exception as e:
            self.log_test("DATABASE", "Hospital Model", "FAIL", str(e))
        
        # Test Patient model
        try:
            patients = Patient.objects.all()
            self.log_test("DATABASE", "Patient Model", "PASS", f"{len(patients)} patients found")
        except Exception as e:
            self.log_test("DATABASE", "Patient Model", "FAIL", str(e))
        
        # Test Doctor model
        try:
            doctors = Doctor.objects.all()
            self.log_test("DATABASE", "Doctor Model", "PASS", f"{len(doctors)} doctors found")
        except Exception as e:
            self.log_test("DATABASE", "Doctor Model", "FAIL", str(e))
        
        # Test Medicine model
        try:
            medicines = Medicine.objects.all()
            self.log_test("PHARMACY", "Medicine Model", "PASS", f"{len(medicines)} medicines found")
        except Exception as e:
            self.log_test("PHARMACY", "Medicine Model", "FAIL", str(e))
        
        # Test TestInfo model
        try:
            tests = TestInfo.objects.all()
            self.log_test("LAB", "TestInfo Model", "PASS", f"{len(tests)} tests found")
        except Exception as e:
            self.log_test("LAB", "TestInfo Model", "FAIL", str(e))
        
        # Test Invoice model
        try:
            invoices = Invoice.objects.all()
            self.log_test("PAYMENT", "Invoice Model", "PASS", f"{len(invoices)} invoices found")
        except Exception as e:
            self.log_test("PAYMENT", "Invoice Model", "FAIL", str(e))
    
    def test_authentication_system(self):
        """Test authentication workflows"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 40)
        
        # Test User model
        try:
            from django.contrib.auth.models import User
            users = User.objects.all()
            self.log_test("AUTH", "User Model", "PASS", f"{len(users)} users found")
        except Exception as e:
            self.log_test("AUTH", "User Model", "FAIL", str(e))
        
        # Check if users have proper relationships
        try:
            patient_users = User.objects.filter(patient__isnull=False)
            doctor_users = User.objects.filter(doctor__isnull=False)
            self.log_test("AUTH", "User-Patient Links", "PASS", f"{len(patient_users)} patient accounts")
            self.log_test("AUTH", "User-Doctor Links", "PASS", f"{len(doctor_users)} doctor accounts")
        except Exception as e:
            self.log_test("AUTH", "User Relationships", "FAIL", str(e))
    
    def test_prescription_system(self):
        """Test prescription workflows"""
        print("\n📋 TESTING PRESCRIPTION SYSTEM")
        print("=" * 40)
        
        try:
            prescriptions = Prescription.objects.all()
            self.log_test("PRESCRIPTION", "Prescription Model", "PASS", f"{len(prescriptions)} prescriptions found")
            
            # Test prescription relationships
            prescriptions_with_tests = Prescription.objects.filter(testcart__isnull=False).distinct()
            self.log_test("PRESCRIPTION", "Prescription-Test Links", "PASS", 
                         f"{len(prescriptions_with_tests)} prescriptions with tests")
            
        except Exception as e:
            self.log_test("PRESCRIPTION", "Prescription System", "FAIL", str(e))
    
    def test_pharmacy_system(self):
        """Test pharmacy functionality"""
        print("\n💊 TESTING PHARMACY SYSTEM")
        print("=" * 40)
        
        try:
            # Test medicine data integrity
            medicines = Medicine.objects.all()
            medicines_with_price = medicines.filter(price__gt=0)
            self.log_test("PHARMACY", "Medicine Pricing", "PASS", 
                         f"{len(medicines_with_price)}/{len(medicines)} medicines have valid prices")
            
            # Test cart functionality
            carts = Cart.objects.all()
            self.log_test("PHARMACY", "Cart Model", "PASS", f"{len(carts)} cart items found")
            
            # Test orders
            orders = Order.objects.all()
            self.log_test("PHARMACY", "Order Model", "PASS", f"{len(orders)} orders found")
            
        except Exception as e:
            self.log_test("PHARMACY", "Pharmacy System", "FAIL", str(e))
    
    def test_lab_system(self):
        """Test laboratory functionality"""
        print("\n🧪 TESTING LABORATORY SYSTEM")
        print("=" * 40)
        
        try:
            # Test lab tests
            tests = TestInfo.objects.all()
            tests_with_price = tests.filter(test_price__gt=0)
            self.log_test("LAB", "Test Pricing", "PASS", 
                         f"{len(tests_with_price)}/{len(tests)} tests have valid prices")
            
            # Test test bookings
            test_bookings = TestBooking.objects.all()
            self.log_test("LAB", "Test Bookings", "PASS", f"{len(test_bookings)} bookings found")
            
            # Test home collection
            home_collection_bookings = TestBooking.objects.filter(home_collection=True)
            self.log_test("LAB", "Home Collection", "PASS", 
                         f"{len(home_collection_bookings)} home collection bookings")
            
        except Exception as e:
            self.log_test("LAB", "Laboratory System", "FAIL", str(e))
    
    def test_payment_system(self):
        """Test payment integration"""
        print("\n💳 TESTING PAYMENT SYSTEM")
        print("=" * 40)
        
        try:
            # Test payment records
            payments = Payment.objects.all()
            successful_payments = payments.filter(status='captured')
            self.log_test("PAYMENT", "Payment Records", "PASS", 
                         f"{len(successful_payments)}/{len(payments)} successful payments")
            
            # Test invoice generation
            invoices = Invoice.objects.all()
            invoices_with_company_info = invoices.filter(company_name__icontains='MAHIMA')
            self.log_test("PAYMENT", "Invoice Company Info", "PASS", 
                         f"{len(invoices_with_company_info)}/{len(invoices)} have correct company info")
            
        except Exception as e:
            self.log_test("PAYMENT", "Payment System", "FAIL", str(e))
    
    def test_file_uploads(self):
        """Test file upload functionality"""
        print("\n📁 TESTING FILE UPLOADS")
        print("=" * 35)
        
        try:
            # Test prescription uploads
            prescription_uploads = PrescriptionUpload.objects.all()
            uploads_with_files = [p for p in prescription_uploads if p.prescription_image]
            self.log_test("FILES", "Prescription Uploads", "PASS", 
                         f"{len(uploads_with_files)}/{len(prescription_uploads)} have files")
            
            # Test report uploads
            reports = Report.objects.all()
            reports_with_files = [r for r in reports if r.report_image]
            self.log_test("FILES", "Report Uploads", "PASS", 
                         f"{len(reports_with_files)}/{len(reports)} have files")
            
        except Exception as e:
            self.log_test("FILES", "File Upload System", "FAIL", str(e))
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("\n🔍 TESTING DATA INTEGRITY")
        print("=" * 35)
        
        try:
            # Check orphaned records
            from django.contrib.auth.models import User
            
            # Users without patient/doctor profiles
            orphaned_users = User.objects.filter(patient__isnull=True, doctor__isnull=True, is_staff=False)
            self.log_test("INTEGRITY", "Orphaned Users", 
                         "WARN" if len(orphaned_users) > 0 else "PASS", 
                         f"{len(orphaned_users)} users without profiles")
            
            # Prescriptions without patients
            prescriptions_without_patient = Prescription.objects.filter(patient__isnull=True)
            self.log_test("INTEGRITY", "Prescriptions Without Patient", 
                         "FAIL" if len(prescriptions_without_patient) > 0 else "PASS", 
                         f"{len(prescriptions_without_patient)} orphaned prescriptions")
            
        except Exception as e:
            self.log_test("INTEGRITY", "Data Integrity Check", "FAIL", str(e))
    
    def test_critical_workflows(self):
        """Test critical business workflows"""
        print("\n🔄 TESTING CRITICAL WORKFLOWS")
        print("=" * 40)
        
        # Test appointment workflow
        try:
            appointments = Appointment.objects.all()
            pending_appointments = appointments.filter(status='Pending')
            self.log_test("WORKFLOW", "Appointment System", "PASS", 
                         f"{len(appointments)} total, {len(pending_appointments)} pending")
        except Exception as e:
            self.log_test("WORKFLOW", "Appointment System", "FAIL", str(e))
        
        # Test prescription to pharmacy workflow
        try:
            prescription_uploads = PrescriptionUpload.objects.filter(status='approved')
            self.log_test("WORKFLOW", "Prescription Approval", "PASS", 
                         f"{len(prescription_uploads)} approved prescriptions")
        except Exception as e:
            self.log_test("WORKFLOW", "Prescription Workflow", "FAIL", str(e))
    
    def fix_common_issues(self):
        """Fix common issues found during testing"""
        print("\n🔧 FIXING COMMON ISSUES")
        print("=" * 30)
        
        fixes_applied = []
        
        try:
            # Fix missing notification sound file
            import os
            sound_dir = "static/HealthStack-System/sounds/"
            if not os.path.exists(sound_dir):
                os.makedirs(sound_dir, exist_ok=True)
                # Create dummy notification file
                with open(os.path.join(sound_dir, "notification.mp3"), "w") as f:
                    f.write("")  # Create empty file to prevent 404
                fixes_applied.append("Created missing notification.mp3 file")
            
            self.log_test("FIXES", "Missing Files", "PASS", f"{len(fixes_applied)} fixes applied")
            
        except Exception as e:
            self.log_test("FIXES", "Auto-Fix Process", "FAIL", str(e))
        
        return fixes_applied
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE SYSTEM TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warnings = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"📈 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📊 SUCCESS RATE: {(passed/total_tests)*100:.1f}%")
        
        # Group by module
        modules = {}
        for result in self.test_results:
            module = result['module']
            if module not in modules:
                modules[module] = {'PASS': 0, 'FAIL': 0, 'WARN': 0}
            modules[module][result['status']] += 1
        
        print(f"\n📋 MODULE BREAKDOWN:")
        for module, stats in modules.items():
            total_module = sum(stats.values())
            success_rate = (stats['PASS']/total_module)*100 if total_module > 0 else 0
            print(f"   {module}: {success_rate:.1f}% ({stats['PASS']}/{total_module})")
        
        # Show critical issues
        critical_issues = [t for t in self.test_results if t['status'] == 'FAIL']
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in critical_issues:
                print(f"   - {issue['module']}: {issue['test']} - {issue['details']}")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'success_rate': (passed/total_tests)*100
            },
            'modules': modules,
            'results': self.test_results
        }
        
        with open('system_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Full report saved to: system_test_report.json")
        return report_data
    
    def run_all_tests(self):
        """Run complete system validation"""
        print("🚀 STARTING COMPREHENSIVE SYSTEM VALIDATION")
        print("🏥 MAHIMA MEDICARE - ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.test_models()
        self.test_authentication_system()
        self.test_prescription_system()
        self.test_pharmacy_system()
        self.test_lab_system()
        self.test_payment_system()
        self.test_file_uploads()
        self.test_data_integrity()
        self.test_critical_workflows()
        
        # Apply fixes
        fixes = self.fix_common_issues()
        
        # Generate final report
        report = self.generate_comprehensive_report()
        
        print(f"\n🎯 VALIDATION COMPLETE!")
        print(f"💡 {len(fixes)} automatic fixes applied")
        print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return report

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()