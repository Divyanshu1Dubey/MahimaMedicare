"""
Simple System Validator - Mahima Medicare
========================================
Quick validation and fixes for critical system components.
"""

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime
import json

class Command(BaseCommand):
    help = 'Quick system validation and fixes'
    
    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Apply fixes')
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 QUICK SYSTEM VALIDATION - MAHIMA MEDICARE")
        self.stdout.write("=" * 50)
        
        issues_found = 0
        fixes_applied = 0
        
        # Test 1: Database connectivity
        try:
            from hospital.models import Patient
            patient_count = Patient.objects.count()
            self.stdout.write(f"✅ Database: {patient_count} patients")
        except Exception as e:
            self.stdout.write(f"❌ Database: {e}")
            issues_found += 1
        
        # Test 2: Models integrity
        try:
            from doctor.models import Doctor_Information
            from pharmacy.models import Medicine
            from hospital_admin.models import Test_Information
            
            doctors = Doctor_Information.objects.count()
            medicines = Medicine.objects.count()
            tests = Test_Information.objects.count()
            
            self.stdout.write(f"✅ Models: {doctors} doctors, {medicines} medicines, {tests} tests")
        except Exception as e:
            self.stdout.write(f"❌ Models: {e}")
            issues_found += 1
        
        # Test 3: URL accessibility
        client = Client()
        urls = ['/', '/login/', '/doctor/', '/pharmacy/']
        
        for url in urls:
            try:
                response = client.get(url)
                if response.status_code in [200, 302]:
                    self.stdout.write(f"✅ URL {url}: {response.status_code}")
                else:
                    self.stdout.write(f"⚠️ URL {url}: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"❌ URL {url}: {e}")
                issues_found += 1
        
        # Test 4: Invoice system
        try:
            from razorpay_payment.models import Invoice
            invoices = Invoice.objects.all()
            
            # Check if invoices have correct company info
            mahima_invoices = invoices.filter(company_name__icontains='MAHIMA')
            
            if invoices.exists() and mahima_invoices.count() < invoices.count():
                self.stdout.write(f"⚠️ Invoice: {mahima_invoices.count()}/{invoices.count()} have correct company info")
                
                # Fix invoices if requested
                if options['fix']:
                    invoices.update(
                        company_name='MAHIMA MEDICARE',
                        company_phone='+91 8763814619',
                        company_email='mahimamedicare01@gmail.com'
                    )
                    fixes_applied += 1
                    self.stdout.write("🔧 Fixed invoice company information")
            else:
                self.stdout.write(f"✅ Invoice: All {invoices.count()} invoices correct")
                
        except Exception as e:
            self.stdout.write(f"❌ Invoice: {e}")
            issues_found += 1
        
        # Test 5: Workflow integrity
        try:
            from doctor.models import Prescription, testCart
            from pharmacy.models import Order
            from razorpay_payment.models import RazorpayPayment
            
            prescriptions = Prescription.objects.count()
            test_carts = testCart.objects.count()
            orders = Order.objects.count()
            payments = RazorpayPayment.objects.count()
            
            self.stdout.write(f"✅ Workflows: {prescriptions} prescriptions, {test_carts} test carts, {orders} orders, {payments} payments")
        except Exception as e:
            self.stdout.write(f"❌ Workflows: {e}")
            issues_found += 1
        
        # Test 6: Security check
        from django.conf import settings
        if settings.DEBUG:
            self.stdout.write("⚠️ Security: DEBUG is enabled (disable for production)")
        else:
            self.stdout.write("✅ Security: DEBUG disabled")
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"📊 SUMMARY: {issues_found} issues found, {fixes_applied} fixes applied")
        
        if issues_found == 0:
            self.stdout.write("🎉 System validation successful!")
            return
        else:
            self.stdout.write(f"⚠️ {issues_found} issues need attention")
            if not options['fix']:
                self.stdout.write("💡 Run with --fix to apply automatic fixes")
        
        # Save simple report
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': issues_found,
            'fixes_applied': fixes_applied,
            'status': 'SUCCESS' if issues_found == 0 else 'ISSUES_FOUND'
        }
        
        with open('quick_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.stdout.write("💾 Report saved to: quick_validation_report.json")