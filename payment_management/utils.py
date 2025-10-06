# Payment Management Utility Functions
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from decimal import Decimal
import uuid
import json

from .models import PaymentRecord, PaymentVerificationLog, DailyPaymentSummary

class PaymentManager:
    """
    Utility class for managing payments across the system
    """
    
    @staticmethod
    def create_payment_record(user, payment_type, payment_method, base_amount, 
                            additional_fees=0, order_reference='', customer_name='', 
                            customer_phone='', customer_address='', **kwargs):
        """
        Create a new payment record for any type of payment in the system
        """
        total_amount = Decimal(str(base_amount)) + Decimal(str(additional_fees))
        
        payment_record = PaymentRecord.objects.create(
            user=user,
            payment_type=payment_type,
            payment_method=payment_method,
            base_amount=Decimal(str(base_amount)),
            additional_fees=Decimal(str(additional_fees)),
            total_amount=total_amount,
            order_reference=order_reference or f"REF_{uuid.uuid4().hex[:8].upper()}",
            customer_name=customer_name or f"{user.first_name} {user.last_name}".strip() or user.username,
            customer_phone=customer_phone or getattr(user, 'phone', ''),
            customer_address=customer_address,
            **kwargs
        )
        
        return payment_record
    
    @staticmethod
    def update_razorpay_details(payment_record, payment_id, order_id=None, signature=None, response_data=None):
        """
        Update payment record with Razorpay transaction details
        """
        payment_record.razorpay_payment_id = payment_id
        if order_id:
            payment_record.razorpay_order_id = order_id
        if signature:
            payment_record.razorpay_signature = signature
        if response_data:
            payment_record.razorpay_response = json.dumps(response_data) if isinstance(response_data, dict) else response_data
        
        payment_record.status = 'received'
        payment_record.payment_received_at = timezone.now()
        payment_record.save()
        
        return payment_record
    
    @staticmethod
    def mark_payment_received(payment_record, admin_user=None, notes=''):
        """
        Mark payment as received (for COD, cash payments)
        """
        previous_status = payment_record.status
        
        payment_record.status = 'received'
        payment_record.payment_received_at = timezone.now()
        if notes:
            payment_record.admin_notes = notes
        payment_record.save()
        
        # Log the action
        if admin_user:
            PaymentVerificationLog.objects.create(
                payment_record=payment_record,
                admin_user=admin_user,
                action_taken='mark_received',
                previous_status=previous_status,
                new_status='received',
                notes=notes
            )
        
        return payment_record
    
    @staticmethod
    def verify_payment(payment_record, admin_user, notes=''):
        """
        Admin verify a payment as legitimate and complete
        """
        previous_status = payment_record.status
        
        payment_record.status = 'verified'
        payment_record.is_admin_verified = True
        payment_record.admin_verified_by = admin_user
        payment_record.admin_verification_date = timezone.now()
        if notes:
            payment_record.admin_notes = notes
        payment_record.save()
        
        # Log the verification
        PaymentVerificationLog.objects.create(
            payment_record=payment_record,
            admin_user=admin_user,
            action_taken='verify',
            previous_status=previous_status,
            new_status='verified',
            notes=notes
        )
        
        # Update daily summary
        PaymentManager.update_daily_summary(payment_record.created_at.date())
        
        return payment_record
    
    @staticmethod
    def update_daily_summary(date):
        """
        Update daily payment summary for dashboard
        """
        payments = PaymentRecord.objects.filter(created_at__date=date)
        
        summary, created = DailyPaymentSummary.objects.get_or_create(
            date=date,
            defaults={
                'total_payments': 0,
                'total_amount': Decimal('0'),
            }
        )
        
        # Calculate totals
        summary.total_payments = payments.count()
        summary.verified_payments = payments.filter(is_admin_verified=True).count()
        summary.pending_payments = payments.filter(status='pending').count()
        summary.failed_payments = payments.filter(status='failed').count()
        
        # Amount totals
        summary.total_amount = payments.aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.verified_amount = payments.filter(is_admin_verified=True).aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.pending_amount = payments.filter(status='pending').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        
        # By payment type
        summary.medicine_amount = payments.filter(payment_type='medicine').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.lab_test_amount = payments.filter(payment_type='lab_test').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.appointment_amount = payments.filter(payment_type='appointment').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        
        # By payment method
        summary.online_amount = payments.filter(payment_method='online').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.cod_amount = payments.filter(payment_method='cod').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        summary.cash_amount = payments.filter(payment_method='cash').aggregate(
            total=Sum('total_amount'))['total'] or Decimal('0')
        
        summary.save()
        return summary


def integrate_with_existing_systems():
    """
    Helper function to integrate payment tracking with existing order systems
    """
    
    # For Lab Test Orders
    def create_lab_test_payment(test_order, payment_method='online'):
        """
        Create payment record for lab test orders
        """
        # Calculate amounts
        base_amount = sum([test.test_price for test in test_order.tests.all()])
        home_collection_fee = 99 if test_order.collection_method == 'home' else 0
        
        payment_record = PaymentManager.create_payment_record(
            user=test_order.user,
            payment_type='lab_test',
            payment_method=payment_method,
            base_amount=base_amount,
            additional_fees=home_collection_fee,
            order_reference=f"LAB_{test_order.pk}",
            customer_name=test_order.patient_name,
            customer_phone=test_order.phone_number,
            customer_address=test_order.address if hasattr(test_order, 'address') else ''
        )
        
        # Link back to test order
        test_order.payment_record = payment_record
        test_order.save()
        
        return payment_record
    
    # For Medicine Orders
    def create_medicine_payment(medicine_order, payment_method='online'):
        """
        Create payment record for medicine orders
        """
        total_amount = medicine_order.final_bill if hasattr(medicine_order, 'final_bill') else medicine_order.total_amount
        
        payment_record = PaymentManager.create_payment_record(
            user=medicine_order.user,
            payment_type='medicine',
            payment_method=payment_method,
            base_amount=total_amount,
            additional_fees=0,
            order_reference=f"MED_{medicine_order.pk}",
            customer_name=f"{medicine_order.user.first_name} {medicine_order.user.last_name}".strip(),
            customer_phone=getattr(medicine_order.user, 'phone', ''),
        )
        
        return payment_record
    
    # For Doctor Appointments
    def create_appointment_payment(appointment, payment_method='online'):
        """
        Create payment record for doctor appointments
        """
        consultation_fee = appointment.doctor.consultation_fee if hasattr(appointment, 'doctor') else 500
        
        payment_record = PaymentManager.create_payment_record(
            user=appointment.patient,
            payment_type='appointment',
            payment_method=payment_method,
            base_amount=consultation_fee,
            additional_fees=0,
            order_reference=f"APT_{appointment.pk}",
            customer_name=f"{appointment.patient.first_name} {appointment.patient.last_name}".strip(),
            customer_phone=getattr(appointment.patient, 'phone', ''),
        )
        
        return payment_record
    
    return {
        'create_lab_test_payment': create_lab_test_payment,
        'create_medicine_payment': create_medicine_payment,
        'create_appointment_payment': create_appointment_payment,
    }