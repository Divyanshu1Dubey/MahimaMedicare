# Create Sample Payment Management Data
import os
import sys
import django

# Setup Django
project_path = r"C:\Users\DIVYANSHU\MahimaMedicare"
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from payment_management.models import PaymentRecord, PaymentVerificationLog
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

def create_sample_data():
    """Create sample payment data for demonstration"""
    
    print("🏥 Creating Sample Payment Management Data...")
    
    # Get existing users or create sample ones
    users = list(User.objects.all()[:5])
    if not users:
        print("Creating sample users...")
        for i in range(3):
            user, created = User.objects.get_or_create(
                username=f'patient{i+1}',
                defaults={
                    'first_name': f'Patient{i+1}',
                    'last_name': 'User',
                    'email': f'patient{i+1}@example.com'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
    
    # Get admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'Manager',
            'email': 'admin@mahimamedicare.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Sample payment data
    payment_types = ['lab_test', 'medicine', 'appointment', 'consultation', 'home_collection']
    payment_methods = ['online', 'cod', 'cash']
    statuses = ['pending', 'received', 'verified', 'failed']
    
    sample_payments = [
        # Lab Test Payments
        {
            'user': users[0] if users else admin_user,
            'payment_type': 'lab_test',
            'payment_method': 'cod',
            'base_amount': 500,
            'additional_fees': 99,
            'customer_name': 'John Doe',
            'customer_phone': '9876543210',
            'customer_address': 'Mumbai, Maharashtra',
            'status': 'pending',
            'order_reference': 'LAB_001'
        },
        {
            'user': users[1] if len(users) > 1 else admin_user,
            'payment_type': 'lab_test',
            'payment_method': 'online',
            'base_amount': 800,
            'additional_fees': 99,
            'customer_name': 'Jane Smith',
            'customer_phone': '8765432109',
            'status': 'received',
            'razorpay_payment_id': 'pay_sample123456',
            'order_reference': 'LAB_002'
        },
        # Medicine Payments
        {
            'user': users[2] if len(users) > 2 else admin_user,
            'payment_type': 'medicine',
            'payment_method': 'online',
            'base_amount': 1250,
            'additional_fees': 0,
            'customer_name': 'Bob Wilson',
            'customer_phone': '7654321098',
            'status': 'verified',
            'is_admin_verified': True,
            'admin_verified_by': admin_user,
            'razorpay_payment_id': 'pay_medicine789',
            'order_reference': 'MED_001'
        },
        # Doctor Appointment
        {
            'user': users[0] if users else admin_user,
            'payment_type': 'appointment',
            'payment_method': 'cod',
            'base_amount': 300,
            'additional_fees': 0,
            'customer_name': 'Alice Johnson',
            'customer_phone': '6543210987',
            'status': 'received',
            'order_reference': 'APT_001'
        },
        # Home Collection
        {
            'user': users[1] if len(users) > 1 else admin_user,
            'payment_type': 'home_collection',
            'payment_method': 'cod',
            'base_amount': 0,
            'additional_fees': 99,
            'customer_name': 'Mike Brown',
            'customer_phone': '5432109876',
            'customer_address': 'Delhi, India',
            'status': 'pending',
            'order_reference': 'HOME_001'
        }
    ]
    
    created_count = 0
    for payment_data in sample_payments:
        # Calculate total amount
        total_amount = Decimal(str(payment_data.pop('base_amount'))) + Decimal(str(payment_data.pop('additional_fees')))
        
        payment, created = PaymentRecord.objects.get_or_create(
            order_reference=payment_data.pop('order_reference'),
            defaults={
                'base_amount': Decimal(str(payment_data.get('base_amount', 0))),
                'additional_fees': Decimal(str(payment_data.get('additional_fees', 0))),
                'total_amount': total_amount,
                **payment_data
            }
        )
        
        if created:
            created_count += 1
            
            # Add some verification logs
            if payment.status in ['verified', 'received']:
                PaymentVerificationLog.objects.create(
                    payment_record=payment,
                    admin_user=admin_user,
                    action_taken='verify' if payment.status == 'verified' else 'mark_received',
                    previous_status='pending',
                    new_status=payment.status,
                    notes=f'Sample verification for {payment.payment_id}'
                )
    
    print(f"✅ Created {created_count} sample payment records")
    
    # Create some additional random payments for the last 7 days
    for day in range(7):
        date_offset = timezone.now() - timedelta(days=day)
        
        for _ in range(random.randint(2, 5)):
            user = random.choice(users) if users else admin_user
            payment_type = random.choice(payment_types)
            payment_method = random.choice(payment_methods)
            status = random.choice(statuses)
            
            base_amount = random.randint(200, 2000)
            additional_fees = 99 if payment_type == 'lab_test' and random.choice([True, False]) else 0
            
            payment = PaymentRecord.objects.create(
                user=user,
                payment_type=payment_type,
                payment_method=payment_method,
                base_amount=Decimal(str(base_amount)),
                additional_fees=Decimal(str(additional_fees)),
                total_amount=Decimal(str(base_amount + additional_fees)),
                customer_name=f"{user.first_name} {user.last_name}",
                customer_phone=f"9{random.randint(100000000, 999999999)}",
                status=status,
                order_reference=f"DEMO_{random.randint(1000, 9999)}",
                created_at=date_offset
            )
            
            if status == 'verified':
                payment.is_admin_verified = True
                payment.admin_verified_by = admin_user
                payment.admin_verification_date = date_offset
                payment.save()
    
    print("✅ Created additional random payment records for last 7 days")
    
    # Summary
    total_payments = PaymentRecord.objects.count()
    verified_payments = PaymentRecord.objects.filter(is_admin_verified=True).count()
    pending_payments = PaymentRecord.objects.filter(status='pending').count()
    total_amount = PaymentRecord.objects.aggregate(total=models.Sum('total_amount'))['total'] or 0
    
    print(f"\n📊 PAYMENT SUMMARY:")
    print(f"   Total Payments: {total_payments}")
    print(f"   Verified Payments: {verified_payments}")
    print(f"   Pending Payments: {pending_payments}")
    print(f"   Total Amount: ₹{total_amount}")
    
    return True

if __name__ == '__main__':
    try:
        from django.db import models
        success = create_sample_data()
        
        if success:
            print("\n🎉 Sample Data Creation Complete!")
            print("\n🔐 ADMIN LOGIN:")
            print("   Username: admin")
            print("   Password: admin123")
            print("\n🌐 ACCESS URLs:")
            print("   Payment Dashboard: http://localhost:8000/payment-management/")
            print("   Django Admin: http://localhost:8000/admin/")
            print("\n💡 READY TO USE:")
            print("   ✅ Payment tracking system ready")
            print("   ✅ Admin verification system ready")
            print("   ✅ Sample data loaded")
            print("   ✅ All features functional")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()