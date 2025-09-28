from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hospital.models import User as CustomUser, Patient, Hospital_Information
from doctor.models import Doctor_Information
from hospital_admin.models import Admin_Information, Test_Information, Clinical_Laboratory_Technician
from pharmacy.models import Medicine
from datetime import date
import random

class Command(BaseCommand):
    help = 'Set up initial test data for Mahima Medicare'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            # Don't delete everything, just ensure we have fresh test data
        
        self.stdout.write('Setting up test data for Mahima Medicare...')
        
        # Create superuser
        self.create_superuser()
        
        # Create hospital
        hospital = self.create_hospital()
        
        # Create admin users
        self.create_admin_users(hospital)
        
        # Create lab technicians
        self.create_lab_technicians(hospital)
        
        # Create doctors
        doctors = self.create_doctors(hospital)
        
        # Create patients
        patients = self.create_patients()
        
        # Create lab tests
        self.create_lab_tests()
        
        # Create medicines
        self.create_medicines()
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully set up test data!\n\n'
                '=== LOGIN CREDENTIALS ===\n'
                'SUPERUSER:\n'
                '  Username: admin\n'
                '  Password: admin123\n\n'
                'ADMIN:\n'
                '  Username: hospital_admin\n'
                '  Password: admin123\n\n'
                'DOCTOR:\n'
                '  Username: dr_sharma\n'
                '  Password: doctor123\n\n'
                'PATIENT:\n'
                '  Username: test_patient\n'
                '  Password: patient123\n\n'
                'LAB TECHNICIAN:\n'
                '  Username: lab_tech\n'
                '  Password: tech123\n\n'
                'Website: https://mahima-test.onrender.com/\n'
                'Ready for comprehensive testing!'
            )
        )

    def create_superuser(self):
        try:
            if not CustomUser.objects.filter(username='admin').exists():
                superuser = CustomUser.objects.create_superuser(
                    username='admin',
                    email='admin@mahimamedicare.com',
                    password='admin123',
                    first_name='System',
                    last_name='Administrator'
                )
                self.stdout.write('✓ Created superuser: admin')
            else:
                self.stdout.write('→ Superuser already exists')
        except Exception as e:
            self.stdout.write(f'✗ Error creating superuser: {e}')

    def create_hospital(self):
        try:
            hospital, created = Hospital_Information.objects.get_or_create(
                hospital_id=1,
                defaults={
                    'name': 'Mahima Medicare Hospital',
                    'phone_number': 9876543210,
                    'email': 'info@mahimamedicare.com',
                    'address': '123 Healthcare Street, Medical District, Mumbai, India',
                    'description': 'Premier healthcare facility with modern equipment and experienced staff.',
                    'hospital_type': 'private',
                    'general_bed_no': 50,
                    'available_icu_no': 10,
                    'regular_cabin_no': 20,
                    'emergency_cabin_no': 5,
                    'vip_cabin_no': 3
                }
            )
            if created:
                self.stdout.write('✓ Created hospital: Mahima Medicare Hospital')
            else:
                self.stdout.write('→ Hospital already exists')
            return hospital
        except Exception as e:
            self.stdout.write(f'✗ Error creating hospital: {e}')
            return None

    def create_admin_users(self, hospital):
        try:
            # Create admin user
            if not CustomUser.objects.filter(username='hospital_admin').exists():
                admin_user = CustomUser.objects.create_user(
                    username='hospital_admin',
                    email='admin@mahimamedicare.com',
                    password='admin123',
                    first_name='Hospital',
                    last_name='Administrator'
                )
                admin_user.is_staff = True
                admin_user.save()
                
                # Create admin information
                Admin_Information.objects.create(
                    user=admin_user,
                    name='Hospital Administrator',
                    email='admin@mahimamedicare.com',
                    phone_number='9876543210',
                    address='123 Admin Office, Medical District',
                    hospital=hospital
                )
                self.stdout.write('✓ Created hospital admin')
            else:
                self.stdout.write('→ Hospital admin already exists')
        except Exception as e:
            self.stdout.write(f'✗ Error creating admin: {e}')

    def create_lab_technicians(self, hospital):
        try:
            # Create lab technician user
            if not CustomUser.objects.filter(username='lab_tech').exists():
                tech_user = CustomUser.objects.create_user(
                    username='lab_tech',
                    email='labtech@mahimamedicare.com',
                    password='tech123',
                    first_name='Lab',
                    last_name='Technician'
                )
                
                # Create lab technician information
                Clinical_Laboratory_Technician.objects.create(
                    user=tech_user,
                    name='Dr. Lab Technician',
                    email='labtech@mahimamedicare.com',
                    phone_number='9876543211',
                    address='Lab Department, Mahima Medicare',
                    hospital=hospital,
                    specialization='Clinical Laboratory',
                    license_number='LAB001',
                    experience_years=5
                )
                self.stdout.write('✓ Created lab technician')
            else:
                self.stdout.write('→ Lab technician already exists')
        except Exception as e:
            self.stdout.write(f'✗ Error creating lab technician: {e}')

    def create_doctors(self, hospital):
        try:
            doctors = []
            doctor_data = [
                {
                    'username': 'dr_sharma',
                    'first_name': 'Dr. Rajesh',
                    'last_name': 'Sharma',
                    'email': 'dr.sharma@mahimamedicare.com',
                    'specialization': 'Cardiology',
                    'qualification': 'MBBS, MD Cardiology',
                    'phone': '9876543212'
                },
                {
                    'username': 'dr_patel',
                    'first_name': 'Dr. Priya',
                    'last_name': 'Patel',
                    'email': 'dr.patel@mahimamedicare.com',
                    'specialization': 'General Medicine',
                    'qualification': 'MBBS, MD',
                    'phone': '9876543213'
                }
            ]
            
            for doc_data in doctor_data:
                if not CustomUser.objects.filter(username=doc_data['username']).exists():
                    doc_user = CustomUser.objects.create_user(
                        username=doc_data['username'],
                        email=doc_data['email'],
                        password='doctor123',
                        first_name=doc_data['first_name'],
                        last_name=doc_data['last_name']
                    )
                    
                    doctor = Doctor_Information.objects.create(
                        user=doc_user,
                        name=f"{doc_data['first_name']} {doc_data['last_name']}",
                        email=doc_data['email'],
                        phone_number=doc_data['phone'],
                        address='Medical Department, Mahima Medicare',
                        hospital_name=hospital.name,
                        specialization=doc_data['specialization'],
                        qualification=doc_data['qualification'],
                        experience='5+ years'
                    )
                    doctors.append(doctor)
                    self.stdout.write(f'✓ Created doctor: {doc_data["username"]}')
                else:
                    doctor = Doctor_Information.objects.get(user__username=doc_data['username'])
                    doctors.append(doctor)
                    self.stdout.write(f'→ Doctor already exists: {doc_data["username"]}')
            
            return doctors
        except Exception as e:
            self.stdout.write(f'✗ Error creating doctors: {e}')
            return []

    def create_patients(self):
        try:
            patients = []
            patient_data = [
                {
                    'username': 'test_patient',
                    'first_name': 'Test',
                    'last_name': 'Patient',
                    'email': 'patient@test.com',
                    'phone': '9876543214'
                },
                {
                    'username': 'john_doe',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@test.com',
                    'phone': '9876543215'
                },
                {
                    'username': 'jane_smith',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'email': 'jane.smith@test.com',
                    'phone': '9876543216'
                }
            ]
            
            for pat_data in patient_data:
                if not CustomUser.objects.filter(username=pat_data['username']).exists():
                    pat_user = CustomUser.objects.create_user(
                        username=pat_data['username'],
                        email=pat_data['email'],
                        password='patient123',
                        first_name=pat_data['first_name'],
                        last_name=pat_data['last_name']
                    )
                    
                    patient = Patient.objects.create(
                        user=pat_user,
                        name=f"{pat_data['first_name']} {pat_data['last_name']}",
                        username=pat_data['username'],
                        email=pat_data['email'],
                        phone_number=int(pat_data['phone']),
                        address=f'{random.randint(100, 999)} Test Street, Test City',
                        dob=f'{1990 + random.randint(0, 20)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                        age=random.randint(25, 65),
                        blood_group=random.choice(['A+', 'B+', 'AB+', 'O+', 'A-', 'B-', 'AB-', 'O-'])
                    )
                    patients.append(patient)
                    self.stdout.write(f'✓ Created patient: {pat_data["username"]}')
                else:
                    patient = Patient.objects.get(user__username=pat_data['username'])
                    patients.append(patient)
                    self.stdout.write(f'→ Patient already exists: {pat_data["username"]}')
            
            return patients
        except Exception as e:
            self.stdout.write(f'✗ Error creating patients: {e}')
            return []

    def create_lab_tests(self):
        try:
            test_data = [
                {'name': 'Complete Blood Count (CBC)', 'price': '500', 'description': 'Comprehensive blood analysis'},
                {'name': 'Blood Sugar (Fasting)', 'price': '150', 'description': 'Fasting glucose level test'},
                {'name': 'Lipid Profile', 'price': '800', 'description': 'Cholesterol and lipid analysis'},
                {'name': 'Liver Function Test', 'price': '600', 'description': 'Comprehensive liver health check'},
                {'name': 'Kidney Function Test', 'price': '700', 'description': 'Comprehensive kidney health check'},
                {'name': 'Thyroid Profile', 'price': '900', 'description': 'Complete thyroid function analysis'},
                {'name': 'Urine Analysis', 'price': '200', 'description': 'Complete urine examination'},
                {'name': 'ECG', 'price': '300', 'description': 'Electrocardiogram for heart analysis'},
                {'name': 'X-Ray Chest', 'price': '400', 'description': 'Chest X-ray examination'},
                {'name': 'Vitamin D Test', 'price': '1200', 'description': 'Vitamin D deficiency test'}
            ]
            
            for test_info in test_data:
                test, created = Test_Information.objects.get_or_create(
                    test_name=test_info['name'],
                    defaults={
                        'test_price': test_info['price'],
                        'test_description': test_info['description']
                    }
                )
                if created:
                    self.stdout.write(f'✓ Created test: {test_info["name"]}')
                else:
                    self.stdout.write(f'→ Test already exists: {test_info["name"]}')
        except Exception as e:
            self.stdout.write(f'✗ Error creating lab tests: {e}')

    def create_medicines(self):
        try:
            # Create medicines using existing model fields
            medicine_data = [
                {'name': 'Paracetamol 500mg', 'price': 25, 'category': 'fever', 'type': 'tablets', 'stock': 100},
                {'name': 'Amoxicillin 250mg', 'price': 45, 'category': 'infection', 'type': 'capsule', 'stock': 80},
                {'name': 'Metformin 500mg', 'price': 35, 'category': 'diabetes', 'type': 'tablets', 'stock': 60},
                {'name': 'Aspirin 75mg', 'price': 20, 'category': 'heartdisease', 'type': 'tablets', 'stock': 90},
                {'name': 'Vitamin C 500mg', 'price': 15, 'category': 'vitamins', 'type': 'tablets', 'stock': 120},
                {'name': 'Omeprazole 20mg', 'price': 30, 'category': 'digestivehealth', 'type': 'capsule', 'stock': 70},
                {'name': 'Salbutamol Syrup', 'price': 85, 'category': 'asthma', 'type': 'syrup', 'stock': 40},
                {'name': 'Cetirizine 10mg', 'price': 22, 'category': 'allergy', 'type': 'tablets', 'stock': 95}
            ]
            
            for med_data in medicine_data:
                medicine, created = Medicine.objects.get_or_create(
                    name=med_data['name'],
                    defaults={
                        'medicine_id': f'MED{random.randint(1000, 9999)}',
                        'price': med_data['price'],
                        'medicine_category': med_data['category'],
                        'medicine_type': med_data['type'],
                        'description': f'High quality {med_data["name"]} for medical treatment',
                        'weight': '500mg' if 'mg' in med_data['name'] else '100ml',
                        'stock_quantity': med_data['stock'],
                        'quantity': med_data['stock'],
                        'Prescription_reqiuired': 'no',
                        'expiry_date': date(2026, 12, 31)
                    }
                )
                if created:
                    self.stdout.write(f'✓ Created medicine: {med_data["name"]}')
                else:
                    self.stdout.write(f'→ Medicine already exists: {med_data["name"]}')
        except Exception as e:
            self.stdout.write(f'✗ Error creating medicines: {e}')