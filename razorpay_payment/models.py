from django.db import models
from doctor.models import Appointment, testOrder, Prescription
from hospital.models import Patient
from pharmacy.models import Order

# Create your models here.

class RazorpayPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('pharmacy', 'Pharmacy'),
        ('test', 'Test'),
        ('prescription', 'Prescription'),
    ]

    payment_id = models.AutoField(primary_key=True)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    
    # Foreign Keys
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    test_order = models.ForeignKey(testOrder, on_delete=models.SET_NULL, null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='created')
    
    # Customer Details
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Info
    notes = models.JSONField(null=True, blank=True)
    receipt = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.razorpay_order_id} - {self.payment_type} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']


class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Invoice Details
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='paid')
    
    # Related Payment
    payment = models.OneToOneField(RazorpayPayment, on_delete=models.CASCADE, related_name='invoice')
    
    # Customer Details (copied from payment for record keeping)
    customer_name = models.CharField(max_length=255)
    customer_email = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(null=True, blank=True)
    
    # Business Details (fixed)
    company_name = models.CharField(max_length=255, default='M/S MAHIMA MEDICARE')
    company_address = models.TextField(default='ORTI, BAGHUNI, NEMALA, CUTTACK')
    company_phone = models.CharField(max_length=20, default='9348221721')
    license_no = models.CharField(max_length=100, default='CU-VI46219/R, 42220/RC, 20123RX')
    gstin = models.CharField(max_length=20, default='21AXRPN9340C1ZH')
    state_code = models.CharField(max_length=5, default='21')
    
    # Invoice Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional Info
    notes = models.TextField(null=True, blank=True)
    terms_conditions = models.TextField(null=True, blank=True, default='Payment is due within 30 days. Thank you for your business!')
    
    # File Storage
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        import random
        import string
        
        # Format: INV-YYYY-MM-XXXXX
        now = datetime.now()
        random_suffix = ''.join(random.choices(string.digits, k=5))
        return f"INV-{now.year}-{now.month:02d}-{random_suffix}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional details for different payment types
    item_type = models.CharField(max_length=50, null=True, blank=True)  # 'appointment', 'medicine', 'test'
    item_id = models.PositiveIntegerField(null=True, blank=True)  # ID of the related item
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - ₹{self.total_price}"
