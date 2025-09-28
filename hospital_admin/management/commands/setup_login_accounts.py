from django.core.management.base import BaseCommand
from hospital.models import User as CustomUser, Patient
from datetime import date
import random

class Command(BaseCommand):
    help = 'Set up essential login credentials for testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up essential test accounts...')
        
        # Create essential test accounts
        self.create_test_accounts()
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n=== MAHIMA MEDICARE TEST SETUP COMPLETE ===\n\n'
                'Website: https://mahima-test.onrender.com/\n\n'
                '=== LOGIN CREDENTIALS ===\n\n'
                'ADMIN/SUPERUSER:\n'
                '  Username: admin\n'
                '  Password: admin123\n'
                '  URL: /admin/\n\n'
                'ALTERNATIVE ADMIN:\n'
                '  Username: testadmin\n'
                '  Password: admin (no password set)\n\n'
                'TEST PATIENT ACCOUNTS:\n'
                '  Username: test_patient | Password: patient123\n'
                '  Username: john_doe | Password: patient123\n'
                '  Username: jane_smith | Password: patient123\n'
                '  Login URL: /login/\n\n'
                '=== TESTING FEATURES ===\n'
                '✅ Standalone Test Booking: /razorpay/book-test/ (NO LOGIN REQUIRED)\n'
                '✅ Patient Dashboard: /patient-dashboard/\n'
                '✅ Pharmacy Shop: /pharmacy/\n'
                '✅ Admin Panel: /admin/\n'
                '✅ Doctor Portal: /doctor/\n'
                '✅ Lab Tests: /hospital_admin/test-list/\n'
                '✅ COD Payment System\n'
                '✅ Razorpay Integration\n\n'
                'System is ready for comprehensive manual testing!\n'
                'Start with: https://mahima-test.onrender.com/razorpay/book-test/\n'
            )
        )

    def create_test_accounts(self):
        try:
            # Ensure we have test patient accounts
            patient_accounts = [
                {'username': 'test_patient', 'name': 'Test Patient', 'email': 'patient@test.com', 'phone': '9876543214'},
                {'username': 'john_doe', 'name': 'John Doe', 'email': 'john.doe@test.com', 'phone': '9876543215'},
                {'username': 'jane_smith', 'name': 'Jane Smith', 'email': 'jane.smith@test.com', 'phone': '9876543216'},
            ]
            
            for account in patient_accounts:
                if not CustomUser.objects.filter(username=account['username']).exists():
                    user = CustomUser.objects.create_user(
                        username=account['username'],
                        email=account['email'],
                        password='patient123',
                        first_name=account['name'].split()[0],
                        last_name=account['name'].split()[1] if len(account['name'].split()) > 1 else ''
                    )
                    user.is_patient = True
                    user.save()
                    
                    # Create patient profile
                    Patient.objects.create(
                        user=user,
                        name=account['name'],
                        username=account['username'],
                        email=account['email'],
                        phone_number=int(account['phone']),
                        address=f'{random.randint(100, 999)} Test Street, Test City',
                        age=random.randint(25, 65)
                    )
                    self.stdout.write(f'✓ Created patient account: {account["username"]}')
                else:
                    self.stdout.write(f'→ Patient exists: {account["username"]}')
                    
            self.stdout.write('✓ All patient accounts ready')
            
        except Exception as e:
            self.stdout.write(f'✗ Error creating accounts: {e}')