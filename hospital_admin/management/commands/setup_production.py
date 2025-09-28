from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from hospital.models import Patient, Hospital_Information
from hospital_admin.models import Test_Information
from pharmacy.models import Medicine
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up production environment with clean data'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Setting up PRODUCTION environment for Mahima Medicare...')
        
        # Create superuser
        self.create_admin_user()
        
        # Create test data
        self.create_basic_data()
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 PRODUCTION ENVIRONMENT READY!\n\n'
                '=== ADMIN LOGIN ===\n'
                'Username: admin\n'
                'Password: mahima2025\n\n'
                '=== TESTING CREDENTIALS ===\n'
                'Patient Username: patient\n'
                'Patient Password: test123\n\n'
                'Website: https://mahima-test.onrender.com/\n\n'
                '✅ Features Available:\n'
                '- Standalone Test Booking (no login required)\n'
                '- COD Payment System\n'
                '- Razorpay Integration\n'
                '- Pharmacy Management\n'
                '- Lab Test Management\n'
                '- Admin Dashboard\n\n'
                'Ready for live testing!'
            )
        )

    def create_admin_user(self):
        try:
            if not User.objects.filter(username='admin').exists():
                admin = User.objects.create_superuser(
                    username='admin',
                    email='admin@mahimamedicare.com',
                    password='mahima2025',
                    first_name='System',
                    last_name='Administrator'
                )
                self.stdout.write('✓ Created admin user')
            else:
                self.stdout.write('→ Admin user already exists')
        except Exception as e:
            self.stdout.write(f'Error creating admin: {e}')

    def create_basic_data(self):
        try:
            # Create a test patient
            if not User.objects.filter(username='patient').exists():
                patient_user = User.objects.create_user(
                    username='patient',
                    email='patient@test.com',
                    password='test123',
                    first_name='Test',
                    last_name='Patient'
                )
                
                Patient.objects.create(
                    user=patient_user,
                    name='Test Patient',
                    username='patient',
                    email='patient@test.com',
                    phone_number=9876543210,
                    address='123 Test Street',
                    age=30
                )
                self.stdout.write('✓ Created test patient')
            
            # Create basic lab tests
            tests = [
                {'name': 'Complete Blood Count (CBC)', 'price': '500'},
                {'name': 'Blood Sugar Test', 'price': '200'},
                {'name': 'Lipid Profile', 'price': '800'},
                {'name': 'Liver Function Test', 'price': '600'},
                {'name': 'Thyroid Profile', 'price': '900'},
            ]
            
            for test_data in tests:
                Test_Information.objects.get_or_create(
                    test_name=test_data['name'],
                    defaults={'test_price': test_data['price']}
                )
            
            self.stdout.write(f'✓ Created {len(tests)} lab tests')
            
            # Create basic medicines
            medicines = [
                {'name': 'Paracetamol 500mg', 'price': 25, 'category': 'fever', 'type': 'tablets'},
                {'name': 'Amoxicillin 250mg', 'price': 45, 'category': 'infection', 'type': 'capsule'},
                {'name': 'Vitamin C 500mg', 'price': 15, 'category': 'vitamins', 'type': 'tablets'},
            ]
            
            for med_data in medicines:
                Medicine.objects.get_or_create(
                    name=med_data['name'],
                    defaults={
                        'price': med_data['price'],
                        'medicine_category': med_data['category'],
                        'medicine_type': med_data['type'],
                        'stock_quantity': 100,
                        'quantity': 100,
                        'expiry_date': date(2026, 12, 31)
                    }
                )
            
            self.stdout.write(f'✓ Created {len(medicines)} medicines')
            
        except Exception as e:
            self.stdout.write(f'Error creating basic data: {e}')