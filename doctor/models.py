from django.db import models

import uuid

# import django user model
from hospital.models import Hospital_Information, User, Patient
from hospital_admin.models import hospital_department, specialization, service
from django.conf import settings


# # Create your models here.

"""
null=True --> don't require a value when inserting into the database
blank=True --> allow blank value when submitting a form
auto_now_add --> automatically set the value to the current date and time
unique=True --> prevent duplicate values
primary_key=True --> set this field as the primary key
editable=False --> prevent the user from editing this field

django field types --> google it  # every field types has field options
Django automatically creates id field for each model class which will be a PK # primary_key=True --> if u want to set manual
"""
# Create your models here.


class Doctor_Information(models.Model):
    DOCTOR_TYPE = (
        ('Cardiologists', 'Cardiologists'),
        ('Neurologists', 'Neurologists'),
        ('Pediatricians', 'Pediatricians'),
        ('Physiatrists', 'Physiatrists'),
        ('Dermatologists', 'Dermatologists'),
    )
    
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    department = models.CharField(max_length=200, choices=DOCTOR_TYPE, null=True, blank=True)
    department_name = models.ForeignKey(hospital_department, on_delete=models.SET_NULL, null=True, blank=True)
    specialization = models.ForeignKey(specialization, on_delete=models.SET_NULL, null=True, blank=True)

    featured_image = models.ImageField(upload_to='doctors/', default='doctors/user-default.png', null=True, blank=True)
    certificate_image = models.ImageField(upload_to='doctors_certificate/', default='doctors_certificate/default.png', null=True, blank=True)

    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    nid = models.CharField(max_length=200, null=True, blank=True)
    visiting_hour = models.CharField(max_length=200, null=True, blank=True)
    consultation_fee = models.IntegerField(null=True, blank=True)
    report_fee = models.IntegerField(null=True, blank=True)
    dob = models.CharField(max_length=200, null=True, blank=True)
    
    # Education
    institute = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    completion_year = models.CharField(max_length=200, null=True, blank=True)
    
    # work experience
    work_place = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    start_year = models.CharField(max_length=200, null=True, blank=True)
    end_year = models.CharField(max_length=200, null=True, blank=True)
    
    # register_status = models.BooleanField(default=False) default='pending'
    register_status =  models.CharField(max_length=200, null=True, blank=True)
    
    # ForeignKey --> one to one relationship with Hospital_Information model.
    hospital_name = models.ForeignKey(Hospital_Information, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.user and hasattr(self.user, 'username') and self.user.username:
            return str(self.user.username)
        elif self.name:
            return str(self.name)
        return f"Doctor #{self.doctor_id}"


class Appointment(models.Model):
    # ('database value', 'display_name')
    APPOINTMENT_TYPE = (
        ('report', 'report'),
        ('checkup', 'checkup'),
    )
    APPOINTMENT_STATUS = (
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
    )

    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    time = models.CharField(max_length=200, null=True, blank=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    appointment_type = models.CharField(max_length=200, choices=APPOINTMENT_TYPE)
    appointment_status = models.CharField(max_length=200, choices=APPOINTMENT_STATUS)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(max_length=200, null=True, blank=True, default='pending')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return str(self.patient.username)

class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    institute = models.CharField(max_length=200, null=True, blank=True)
    year_of_completion = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.doctor.name)
    
class Experience(models.Model):
    experience_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    work_place_name = models.CharField(max_length=200, null=True, blank=True)
    from_year = models.CharField(max_length=200, null=True, blank=True)
    to_year = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.doctor.name)


class Report(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', 'Pending Collection'),
        ('collected', 'Sample Collected'),
        ('processing', 'Under Processing'),
        ('completed', 'Report Ready'),
        ('delivered', 'Report Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT'),
    ]
    
    report_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    
    # Lab technician assignment
    assigned_technician = models.ForeignKey('hospital_admin.Clinical_Laboratory_Technician', 
                                          on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='assigned_reports')
    
    # Test order reference
    test_order = models.ForeignKey('testOrder', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Report status and tracking
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Specimen information
    specimen_id = models.CharField(max_length=200, null=True, blank=True)
    specimen_type = models.CharField(max_length=200, null=True, blank=True)
    collection_date = models.DateTimeField(null=True, blank=True)
    receiving_date = models.DateTimeField(null=True, blank=True)
    
    # Test details
    test_name = models.CharField(max_length=200, null=True, blank=True)
    result = models.TextField(null=True, blank=True)  # Changed to TextField for longer results
    unit = models.CharField(max_length=200, null=True, blank=True)
    referred_value = models.CharField(max_length=200, null=True, blank=True)
    
    # Delivery information
    delivery_date = models.DateTimeField(null=True, blank=True)
    other_information = models.TextField(null=True, blank=True)
    
    # File and timestamps
    report_pdf = models.FileField(upload_to='lab_reports/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification flags
    patient_notified = models.BooleanField(default=False)
    doctor_notified = models.BooleanField(default=False)
    
    # Comments and notes
    lab_notes = models.TextField(null=True, blank=True, help_text="Internal lab notes")
    technician_comments = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Report #{self.report_id} - {self.patient.username if self.patient else 'No Patient'}"
    
    def get_status_display_color(self):
        """Return Bootstrap color class for status"""
        status_colors = {
            'pending': 'warning',
            'collected': 'info',
            'processing': 'primary',
            'completed': 'success',
            'delivered': 'secondary',
            'cancelled': 'danger',
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_priority_display_color(self):
        """Return Bootstrap color class for priority"""
        priority_colors = {
            'normal': 'secondary',
            'urgent': 'warning',
            'stat': 'danger',
        }
        return priority_colors.get(self.priority, 'secondary')
    
    def can_upload_report(self):
        """Check if report can be uploaded"""
        return self.status in ['collected', 'processing']
    
    def can_deliver_report(self):
        """Check if report can be delivered"""
        return self.status == 'completed' and self.report_pdf

class Specimen(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    specimen_id = models.AutoField(primary_key=True)
    specimen_type = models.CharField(max_length=200, null=True, blank=True)
    collection_date = models.CharField(max_length=200, null=True, blank=True)
    receiving_date = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.report.report_id)

class Test(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    result = models.CharField(max_length=200, null=True, blank=True)
    unit = models.CharField(max_length=200, null=True, blank=True)
    referred_value = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.report.report_id)

        
class Prescription(models.Model):
    # medicine name, quantity, days, time, description, test, test_descrip
    prescription_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    create_date = models.CharField(max_length=200, null=True, blank=True)
    medicine_name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    days = models.CharField(max_length=200, null=True, blank=True)
    time = models.CharField(max_length=200, null=True, blank=True)
    relation_with_meal = models.CharField(max_length=200, null=True, blank=True)
    medicine_description = models.TextField(null=True, blank=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    test_description = models.TextField(null=True, blank=True)
    extra_information = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.patient and hasattr(self.patient, 'username') and self.patient.username:
            return str(self.patient.username)
        return f"Prescription #{self.prescription_id}"

class Prescription_medicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
    medicine_id = models.AutoField(primary_key=True)
    medicine_name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    duration = models.CharField(max_length=200, null=True, blank=True)
    frequency = models.CharField(max_length=200, null=True, blank=True)
    relation_with_meal = models.CharField(max_length=200, null=True, blank=True)
    instruction = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.prescription.prescription_id)

class Prescription_test(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('refunded', 'Refunded'),
    ]
    
    TEST_STATUS_CHOICES = [
        ('prescribed', 'Prescribed'),
        ('paid', 'Payment Completed'),
        ('collected', 'Sample Collected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('delivered', 'Report Delivered'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    test_description = models.TextField(null=True, blank=True)
    test_info_id = models.CharField(max_length=200, null=True, blank=True)
    test_info_price = models.CharField(max_length=200, null=True, blank=True)
    test_info_pay_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    # Enhanced tracking fields
    test_status = models.CharField(max_length=20, choices=TEST_STATUS_CHOICES, default='prescribed')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Lab assignment
    assigned_technician = models.ForeignKey(
        'hospital_admin.Clinical_Laboratory_Technician', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tests'
    )
    
    """
    (create prescription)
    doctor input --> test_id 
    using test_id --> retrive price
    store price in prescription_test column
    """

    def __str__(self):
        return str(self.prescription.prescription_id)
    
# # test cart system
class testCart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_cart')
    item = models.ForeignKey(Prescription_test, on_delete=models.CASCADE)
    name = models.CharField(default='test', max_length=200)
    purchased = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.item.test_info_id} X {self.item.test_name}'

    @property
    def total(self):
        # Kung may string unit, tanggalin at gawing float
        price_str = str(self.item.test_info_price)
        price_numeric = price_str.split()[0]  # "233.0 INR" -> "233.0"
        return float(price_numeric)


class testOrder(models.Model):
    COLLECTION_CHOICES = [
        ('center', 'Collection at Center'),
        ('home', 'Home Sample Collection'),
    ]
    
    orderitems = models.ManyToManyField(testCart)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=200, blank=True, null=True)
    trans_ID = models.CharField(max_length=200, blank=True, null=True)
    
    # Home Sample Collection Fields
    collection_type = models.CharField(max_length=20, choices=COLLECTION_CHOICES, default='center')
    home_collection_fee = models.DecimalField(max_digits=10, decimal_places=2, default=99.00)
    collection_address = models.TextField(blank=True, null=True)
    preferred_collection_date = models.DateField(blank=True, null=True)
    preferred_collection_time = models.TimeField(blank=True, null=True)
    collection_status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'Collection in Progress'),
        ('collected', 'Sample Collected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])

    @property
    def total_amount(self):
        return sum(cart.total for cart in self.orderitems.all())
    
    @property
    def tests_subtotal(self):
        """Get only tests total without home collection fee"""
        return self.total_amount

    @property
    def home_collection_charge(self):
        """Get home collection fee if applicable"""
        if self.collection_type == 'home':
            return self.home_collection_fee
        return 0.0

    @property
    def final_bill(self):
        from decimal import Decimal
        
        # Convert all to Decimal for consistent calculation
        total = Decimal(str(self.total_amount or 0))
        home_charge = Decimal(str(self.home_collection_charge or 0))
        
        # No VAT for lab tests as per user request
        base_total = total + home_charge
        return float(base_total)
    
    def get_collection_display(self):
        """Get human-readable collection type"""
        return dict(self.COLLECTION_CHOICES).get(self.collection_type, 'Unknown')


class Doctor_review(models.Model):
    review_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(max_length=1000, null=True, blank=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # Only show verified reviews

    class Meta:
        unique_together = ('doctor', 'patient')  # One review per patient per doctor
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.patient.name} for Dr. {self.doctor.name}"