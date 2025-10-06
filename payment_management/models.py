# Payment Verification and Management System
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

User = get_user_model()

class PaymentRecord(models.Model):
    """
    Master Payment Record - All payments (medicine, lab tests, appointments, etc.)
    """
    PAYMENT_TYPES = [
        ('medicine', 'Medicine Order'),
        ('lab_test', 'Lab Test'),
        ('appointment', 'Doctor Appointment'),
        ('consultation', 'Doctor Consultation'),
        ('home_collection', 'Home Sample Collection'),
        ('other', 'Other Services'),
    ]
    
    PAYMENT_METHODS = [
        ('online', 'Online Payment (Razorpay)'),
        ('cod', 'Cash on Delivery'),
        ('cash', 'Direct Cash'),
        ('card', 'Card Payment'),
        ('upi', 'UPI Payment'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Payment Pending'),
        ('received', 'Payment Received'),
        ('verified', 'Payment Verified by Admin'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded'),
        ('disputed', 'Payment Disputed'),
    ]
    
    # Basic Information
    payment_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Amount Details
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    additional_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and Verification
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    is_admin_verified = models.BooleanField(default=False)
    admin_verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_payments'
    )
    admin_verification_date = models.DateTimeField(null=True, blank=True)
    
    # Razorpay Details (if online payment)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)
    razorpay_response = models.JSONField(null=True, blank=True)
    
    # Reference Information
    order_reference = models.CharField(max_length=100)  # Medicine order ID, test order ID, etc.
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField(blank=True)
    
    # Timestamps
    payment_initiated_at = models.DateTimeField(auto_now_add=True)
    payment_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, help_text="Admin verification notes and comments")
    
    class Meta:
        db_table = 'payment_records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_id} - {self.get_payment_type_display()} - ₹{self.total_amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate unique payment ID
            import uuid
            self.payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class PaymentVerificationLog(models.Model):
    """
    Track all admin actions on payments
    """
    payment_record = models.ForeignKey(PaymentRecord, on_delete=models.CASCADE)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_taken = models.CharField(max_length=50)
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_verification_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.payment_record.payment_id} - {self.action_taken} by {self.admin_user.username}"


class DailyPaymentSummary(models.Model):
    """
    Daily summary for admin dashboard
    """
    date = models.DateField(unique=True)
    
    # Payment Counts
    total_payments = models.IntegerField(default=0)
    verified_payments = models.IntegerField(default=0)
    pending_payments = models.IntegerField(default=0)
    failed_payments = models.IntegerField(default=0)
    
    # Amount Totals
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    verified_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # By Payment Type
    medicine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_test_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    appointment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # By Payment Method
    online_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cod_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_payment_summary'
        ordering = ['-date']
    
    def __str__(self):
        return f"Payment Summary - {self.date} - ₹{self.total_amount}"