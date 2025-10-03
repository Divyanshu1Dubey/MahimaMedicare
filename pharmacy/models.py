from django.db import models
from django.conf import settings
import uuid
from doctor.models import Prescription
from hospital.models import User, Patient


class Pharmacist(models.Model):
    pharmacist_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='pharmacist')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='doctors/', default='pharmacist/user-default.png', null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.user and hasattr(self.user, 'username') and self.user.username:
            return str(self.user.username)
        elif self.name:
            return str(self.name)
        return f"Pharmacist #{self.pharmacist_id}"


class Medicine(models.Model):
    MEDICINE_TYPE = (
        ('tablets', 'tablets'),
        ('syrup', 'syrup'),
        ('capsule', 'capsule'),
        ('general', 'general'),
    )
    REQUIREMENT_TYPE = (
        ('yes', 'yes'),
        ('no', 'no'),
    )
    MEDICINE_CATEGORY = (
        ('fever', 'fever'),
        ('pain', 'pain'),
        ('cough', 'cough'),
        ('cold', 'cold'),
        ('flu', 'flu'),
        ('diabetes', 'diabetes'),
        ('eye', 'eye'),
        ('ear', 'ear'),
        ('allergy', 'allergy'),
        ('asthma', 'asthma'),
        ('bloodpressure', 'bloodpressure'),
        ('heartdisease', 'heartdisease'),
        ('vitamins', 'vitamins'),
        ('digestivehealth', 'digestivehealth'),
        ('skin', 'skin'),
        ('infection', 'infection'),
        ('nurological', 'nurological'),
    )

    serial_number = models.AutoField(primary_key=True)
    medicine_id = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    composition = models.TextField(null=True, blank=True, help_text="Active ingredients and their quantities")
    hsn_code = models.CharField(max_length=20, null=True, blank=True, help_text="HSN code for tax classification")
    weight = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    featured_image = models.ImageField(upload_to='medicines/', default='medicines/default.png', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    medicine_type = models.CharField(max_length=200, choices=MEDICINE_TYPE, null=True, blank=True)
    medicine_category = models.CharField(max_length=200, choices=MEDICINE_CATEGORY, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    stock_quantity = models.IntegerField(null=True, blank=True, default=0)
    Prescription_reqiuired = models.CharField(max_length=200, choices=REQUIREMENT_TYPE, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    @property
    def is_expiring_soon(self):
        from datetime import date, timedelta
        if self.expiry_date:
            # Notify 3 months (90 days) before expiry
            return self.expiry_date <= date.today() + timedelta(days=90)
        return False

    @property
    def days_until_expiry(self):
        from datetime import date
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None

    def __str__(self):
        if self.name and self.composition:
            return f"{self.name} - {self.composition[:50]}{'...' if len(self.composition) > 50 else ''}"
        elif self.name:
            return str(self.name)
        else:
            return f"Medicine #{self.serial_number}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    item = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchased = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity} X {self.item}'

    # Each product total
    def get_total(self):
        return self.item.price * self.quantity


class Order(models.Model):
    DELIVERY_CHOICES = (
        ('pickup', 'Pickup at Pharmacy'),
        ('delivery', 'Home Delivery'),
    )
    
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    orderitems = models.ManyToManyField(Cart)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    # Delivery information
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    delivery_address = models.TextField(blank=True, null=True)
    delivery_phone = models.CharField(max_length=15, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    # Pharmacy processing
    pharmacist_notes = models.TextField(blank=True, null=True)
    estimated_ready_time = models.DateTimeField(blank=True, null=True)

    # Payment info
    payment_status = models.CharField(max_length=200, blank=True, null=True)
    trans_ID = models.CharField(max_length=200, blank=True, null=True)  # legacy field
    payment_session_id = models.CharField(max_length=255, blank=True, null=True)  # PayMongo source ID
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # PayMongo payment ID

    # Subtotal
    def get_totals(self):
        total = 0
        for order_item in self.orderitems.all():
            total += float(order_item.get_total())
        return total

    # Count Cart Items
    def count_cart_items(self):
        return self.orderitems.count()

    # Stock Calculation
    def stock_quantity_decrease(self):
        """Decrease unit quantity for all items in this order with reset logic"""
        from .utils import check_and_reset_medicine_quantity
        
        for order_item in self.orderitems.all():
            medicine = order_item.item
            required_quantity = order_item.quantity
            
            # Check current availability
            if medicine.quantity < required_quantity:
                # Try to reset if quantity is 0
                was_reset, new_quantity, new_stock = check_and_reset_medicine_quantity(medicine)
                
                # If still insufficient after reset, raise error
                if new_quantity < required_quantity:
                    raise ValueError(
                        f"Insufficient stock for {medicine.name}. "
                        f"Available: {new_quantity}, Required: {required_quantity}"
                    )
            
            # Now we have sufficient quantity, proceed with deduction
            medicine.quantity -= required_quantity
            # Keep stock_quantity in sync as a total available snapshot
            if medicine.stock_quantity is not None:
                medicine.stock_quantity = max(0, (medicine.stock_quantity or 0) - required_quantity)
            medicine.save()
            
            # Check if we need another reset after deduction
            if medicine.quantity <= 0:
                check_and_reset_medicine_quantity(medicine)
    
    def check_stock_availability(self):
        """Check if all items in the order have sufficient unit quantity with reset consideration"""
        from .utils import check_and_reset_medicine_quantity
        
        for order_item in self.orderitems.all():
            medicine = order_item.item
            required_quantity = order_item.quantity
            
            # Check current availability
            if medicine.quantity < required_quantity:
                # Try to reset if quantity is 0
                was_reset, new_quantity, new_stock = check_and_reset_medicine_quantity(medicine)
                
                # Check if we have enough after potential reset
                if new_quantity < required_quantity:
                    return False, medicine.name
        
        return True, None

    # GST amount (5%)
    def get_gst_amount(self):
        subtotal = self.get_totals()
        return subtotal * 0.05 if subtotal > 0 else 0
    
    # Cart total (subtotal + GST, without delivery)
    def get_cart_total(self):
        subtotal = self.get_totals()
        gst = self.get_gst_amount()
        return subtotal + gst
    
    # Final Bill with delivery and GST
    def final_bill(self):
        cart_total = self.get_cart_total()
        if cart_total > 0:
            delivery_fee = 40 if self.delivery_method == 'delivery' else 0
            return cart_total + delivery_fee
        return 0