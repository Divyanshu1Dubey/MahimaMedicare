import email
from email.mime import image
from unicodedata import name
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.paginator import Paginator
from hospital.models import Hospital_Information, User, Patient
from django.db.models import Q
from django.utils import timezone
from pharmacy.models import Medicine, Pharmacist
from pharmacy.forms import MedicineForm
from doctor.models import Doctor_Information, Prescription, Prescription_test, Report, Appointment, Experience , Education,Specimen,Test
from pharmacy.models import Order, Cart
from .forms import AdminUserCreationForm, LabWorkerCreationForm, EditHospitalForm, EditEmergencyForm,AdminForm , PharmacistCreationForm 

from .models import Admin_Information,specialization,service,hospital_department, Clinical_Laboratory_Technician, Test_Information
from doctor.models import Prescription_test, Report
import random,re
import string
import uuid
import json
from django.db.models import Count, Q
from django.db.models import Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from datetime import datetime
import datetime
from django.views.decorators.csrf import csrf_exempt

from django.core.mail import BadHeaderError, send_mail
import ssl
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from .utils import searchMedicines

# Create your views here.

@csrf_exempt
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    """Dashboard view for hospital admin - simple landing page"""
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        context = {'admin': user}
        return render(request, 'hospital_admin/dashboard.html', context)
    elif request.user.is_labworker:
        return redirect('labworker-dashboard')
    elif request.user.is_pharmacist:
        return redirect('pharmacist-dashboard')
    else:
        return redirect('admin-logout')

@csrf_exempt
@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    # admin = Admin_Information.objects.get(user_id=pk)
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        total_patient_count = Patient.objects.annotate(count=Count('patient_id'))
        total_doctor_count = Doctor_Information.objects.annotate(count=Count('doctor_id'))
        total_pharmacist_count = Pharmacist.objects.annotate(count=Count('pharmacist_id'))
        total_hospital_count = Hospital_Information.objects.annotate(count=Count('hospital_id'))
        total_labworker_count = Clinical_Laboratory_Technician.objects.annotate(count=Count('technician_id'))
        pending_appointment = Appointment.objects.filter(appointment_status='pending').count()
        doctors = Doctor_Information.objects.all()
        patients = Patient.objects.all()
        hospitals = Hospital_Information.objects.all()
        lab_workers = Clinical_Laboratory_Technician.objects.all()
        pharmacists = Pharmacist.objects.all()
        
        sat_date = datetime.date.today()
        sat_date_str = str(sat_date)
        sat = sat_date.strftime("%A")

        sun_date = sat_date + datetime.timedelta(days=1) 
        sun_date_str = str(sun_date)
        sun = sun_date.strftime("%A")
        
        mon_date = sat_date + datetime.timedelta(days=2) 
        mon_date_str = str(mon_date)
        mon = mon_date.strftime("%A")
        
        tues_date = sat_date + datetime.timedelta(days=3) 
        tues_date_str = str(tues_date)
        tues = tues_date.strftime("%A")
        
        wed_date = sat_date + datetime.timedelta(days=4) 
        wed_date_str = str(wed_date)
        wed = wed_date.strftime("%A")
        
        thurs_date = sat_date + datetime.timedelta(days=5) 
        thurs_date_str = str(thurs_date)
        thurs = thurs_date.strftime("%A")
        
        fri_date = sat_date + datetime.timedelta(days=6) 
        fri_date_str = str(fri_date)
        fri = fri_date.strftime("%A")
        
        sat_count = Appointment.objects.filter(date=sat_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        sun_count = Appointment.objects.filter(date=sun_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        mon_count = Appointment.objects.filter(date=mon_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        tues_count = Appointment.objects.filter(date=tues_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        wed_count = Appointment.objects.filter(date=wed_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        thurs_count = Appointment.objects.filter(date=thurs_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        fri_count = Appointment.objects.filter(date=fri_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()

        context = {'admin': user,'total_patient_count': total_patient_count,'total_doctor_count':total_doctor_count,'pending_appointment':pending_appointment,'doctors':doctors,'patients':patients,'hospitals':hospitals,'lab_workers':lab_workers,'total_pharmacist_count':total_pharmacist_count,'total_hospital_count':total_hospital_count,'total_labworker_count':total_labworker_count,'sat_count': sat_count, 'sun_count': sun_count, 'mon_count': mon_count, 'tues_count': tues_count, 'wed_count': wed_count, 'thurs_count': thurs_count, 'fri_count': fri_count, 'sat': sat, 'sun': sun, 'mon': mon, 'tues': tues, 'wed': wed, 'thurs': thurs, 'fri': fri, 'pharmacists': pharmacists}
        return render(request, 'hospital_admin/admin-dashboard.html', context)
    elif request.user.is_labworker:
        # messages.error(request, 'You are not authorized to access this page')
        return redirect('labworker-dashboard')
    else:
        # Handle unauthorized users
        messages.error(request, 'You are not authorized to access this page')
        return redirect('admin_login')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutAdmin(request):
    logout(request)
    messages.error(request, 'User Logged out')
    return redirect('admin_login')
            
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.method == 'GET':
        return render(request, 'hospital_admin/login.html')
    elif request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Check if fields are empty
        if not username:
            messages.error(request, 'Please enter your username.')
            return render(request, 'hospital_admin/login.html')
        
        if not password:
            messages.error(request, 'Please enter your password.')
            return render(request, 'hospital_admin/login.html')

        # Check if user exists (case-insensitive)
        try:
            # First try exact match
            existing_user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Try case-insensitive match
            try:
                existing_user = User.objects.get(username__iexact=username)
                username = existing_user.username  # Use the correct case
            except User.DoesNotExist:
                messages.error(request, f'Username "{username}" does not exist. Please check your spelling.')
                return render(request, 'hospital_admin/login.html')

        # Try to authenticate
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_hospital_admin:
                messages.success(request, f'Welcome back, Admin {user.username}!')
                return redirect('dashboard')
            elif user.is_labworker:
                messages.success(request, f'Welcome back, Lab Worker {user.username}!')
                return redirect('labworker-dashboard')
            elif user.is_pharmacist:
                messages.success(request, f'Welcome back, Pharmacist {user.username}!')
                return redirect('pharmacist-dashboard')
            else:
                messages.error(request, f'Account "{username}" does not have admin, lab worker, or pharmacist privileges.')
                return redirect('admin-logout')
        else:
            messages.error(request, f'Incorrect password for username "{username}". Please check your password and try again.')
        

    return render(request, 'hospital_admin/login.html')


@csrf_exempt
def admin_register(request):
    page = 'hospital_admin/register'
    form = AdminUserCreationForm()

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # form.save()
                # commit=False --> don't save to database yet (we have a chance to modify object)
                user = form.save(commit=False)
                user.is_hospital_admin = True
                user.save()

                messages.success(request, f'Admin account created successfully for "{user.username}"! You can now log in.')
                
                # After user is created, we can log them in
                #login(request, user)
                return redirect('admin_login')
            except Exception as e:
                messages.error(request, f'Account creation failed: {str(e)}')
        else:
            # Show specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f'Registration error: {error}')
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')

    context = {'page': page, 'form': form}
    return render(request, 'hospital_admin/register.html', context)

@csrf_exempt
def admin_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email, is_hospital_admin=True)
                
                # Generate password reset token
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes
                from django.core.mail import send_mail
                from django.conf import settings
                
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset URL (for now, just show the token - you can create a proper reset view later)
                reset_url = f"http://your-domain.com/reset-password/{uid}/{token}/"
                
                # Send email
                subject = 'Password Reset Request - Mahima Medicare'
                message = f'''
                Hello {user.username},
                
                You have requested a password reset for your Mahima Medicare admin account.
                
                Your reset link: {reset_url}
                
                Your temporary reset code: {token[:10]}
                
                If you did not request this reset, please ignore this email.
                
                Best regards,
                Mahima Medicare Team
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Password reset instructions have been sent to {email}')
                return redirect('admin_forgot_password')
                
            except User.DoesNotExist:
                messages.error(request, 'No admin account found with this email address')
            except Exception as e:
                messages.error(request, f'Error sending reset email: {str(e)}')
        else:
            messages.error(request, 'Please enter an email address')
    
    return render(request, 'hospital_admin/forgot-password.html')

@csrf_exempt
@login_required(login_url='admin_login')
def invoice(request):
    return render(request, 'hospital_admin/invoice.html')

@csrf_exempt
@login_required(login_url='admin_login')
def invoice_report(request):
    return render(request, 'hospital_admin/invoice-report.html')

@login_required(login_url='admin_login')
def lock_screen(request):
    return render(request, 'hospital_admin/lock-screen.html')

@csrf_exempt
@login_required(login_url='admin_login')
def patient_list(request):
    user = None
    try:
        if hasattr(request.user, 'is_hospital_admin') and request.user.is_hospital_admin:
            user = Admin_Information.objects.get(user=request.user)
    except Admin_Information.DoesNotExist:
        pass
    patients = Patient.objects.all()
    return render(request, 'hospital_admin/patient-list.html', {'all': patients, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def specialitites(request):
    return render(request, 'hospital_admin/specialities.html')

@csrf_exempt
@login_required(login_url='admin_login')
def appointment_list(request):
    return render(request, 'hospital_admin/appointment-list.html')

@login_required(login_url='admin_login')
def transactions_list(request):
    return render(request, 'hospital_admin/transactions-list.html')

@csrf_exempt
@login_required(login_url='admin_login')
def emergency_details(request):
    user = Admin_Information.objects.get(user=request.user)
    hospitals = Hospital_Information.objects.all()
    context = { 'admin': user, 'all': hospitals}
    return render(request, 'hospital_admin/emergency.html', context)

@csrf_exempt
@login_required(login_url='admin_login')
def hospital_list(request):
    user = Admin_Information.objects.get(user=request.user)
    hospitals = Hospital_Information.objects.all()
    context = { 'admin': user, 'hospitals': hospitals}
    return render(request, 'hospital_admin/hospital-list.html', context)

@csrf_exempt
@login_required(login_url='admin_login')
def appointment_list(request):
    return render(request, 'hospital_admin/appointment-list.html')

@csrf_exempt
@login_required(login_url='admin_login')
def hospital_profile(request):
    return render(request, 'hospital-profile.html')

@csrf_exempt
@login_required(login_url='admin_login')
def hospital_admin_profile(request, pk):

    # profile = request.user.profile
    # get user id of logged in user, and get all info from table
    admin = Admin_Information.objects.get(user_id=pk)
    form = AdminForm(instance=admin)

    if request.method == 'POST':
        form = AdminForm(request.POST, request.FILES,
                          instance=admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Updated')
            return redirect('admin-dashboard', pk=pk)
        else:
            form = AdminForm()

    context = {'admin': admin, 'form': form}
    return render(request, 'hospital_admin/hospital-admin-profile.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Hospital_Information, hospital_department, specialization, service, Admin_Information

@csrf_exempt
@login_required(login_url='admin_login')
def add_hospital(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)

        if request.method == 'POST':
            # Handle image upload
            featured_image = request.FILES.get('featured_image', "departments/default.png")

            # Get form data
            hospital_name = request.POST.get('hospital_name')
            address = request.POST.get('address')
            description = request.POST.get('description')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            hospital_type = request.POST.get('type')
            specialization_name = request.POST.getlist('specialization')
            department_name = request.POST.getlist('department')
            service_name = request.POST.getlist('service')

            # Validation: Required fields
            if not hospital_name or not address or not email or not phone_number:
                messages.error(request, "Please fill in all required fields.")
                return redirect('add-hospital')

            # Validate phone number
            try:
                phone_number = int(phone_number)
            except ValueError:
                messages.error(request, "Phone number must be a valid number.")
                return redirect('add-hospital')

            try:
                # Create hospital
                hospital = Hospital_Information(
                    name=hospital_name,
                    description=description,
                    address=address,
                    email=email,
                    phone_number=phone_number,
                    featured_image=featured_image,
                    hospital_type=hospital_type
                )
                hospital.save()

                # Save departments
                for dept_name in department_name:
                    if dept_name.strip():  # skip empty
                        dept = hospital_department(hospital=hospital, hospital_department_name=dept_name)
                        dept.save()

                # Save specializations
                for spec_name in specialization_name:
                    if spec_name.strip():
                        spec = specialization(hospital=hospital, specialization_name=spec_name)
                        spec.save()

                # Save services
                for serv_name in service_name:
                    if serv_name.strip():
                        serv = service(hospital=hospital, service_name=serv_name)
                        serv.save()

                messages.success(request, 'Hospital Added Successfully!')
                return redirect('hospital-list')

            except Exception as e:
                messages.error(request, f"An error occurred while saving the hospital: {e}")
                return redirect('add-hospital')

        context = {'admin': user}
        return render(request, 'hospital_admin/add-hospital.html', context)



# def edit_hospital(request, pk):
#     hospital = Hospital_Information.objects.get(hospital_id=pk)
#     return render(request, 'hospital_admin/edit-hospital.html')

@csrf_exempt
@login_required(login_url='admin_login')
def edit_hospital(request, pk):
    if  request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        hospital = Hospital_Information.objects.get(hospital_id=pk)
        old_featured_image = hospital.featured_image

        if request.method == 'GET':
            specializations = specialization.objects.filter(hospital=hospital)
            services = service.objects.filter(hospital=hospital)
            departments = hospital_department.objects.filter(hospital=hospital)
            context = {'hospital': hospital, 'specializations': specializations, 'services': services,'departments':departments, 'admin': user}
            return render(request, 'hospital_admin/edit-hospital.html',context)

        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image
                               
            hospital_name = request.POST.get('hospital_name')
            address = request.POST.get('address')
            description = request.POST.get('description')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number') 
            hospital_type = request.POST.get('type')
            
            specialization_name = request.POST.getlist('specialization')
            department_name = request.POST.getlist('department')
            service_name = request.POST.getlist('service')

            hospital.name = hospital_name
            hospital.description = description
            hospital.address = address
            hospital.email = email
            hospital.phone_number =phone_number
            hospital.featured_image =featured_image 
            hospital.hospital_type =hospital_type
            
            # specializations.specialization_name=specialization_name
            # services.service_name = service_name
            # departments.hospital_department_name = department_name 

            hospital.save()

            # Specialization
            for i in range(len(specialization_name)):
                specializations = specialization(hospital=hospital)
                specializations.specialization_name = specialization_name[i]
                specializations.save()

            # Experience
            for i in range(len(service_name)):
                services = service(hospital=hospital)
                services.service_name = service_name[i]
                services.save()
                
            for i in range(len(department_name)):
                departments = hospital_department(hospital=hospital)
                departments.hospital_department_name = department_name[i]
                departments.save()

            messages.success(request, 'Hospital Updated')
            return redirect('hospital-list')

@csrf_exempt
@login_required(login_url='admin_login')
def delete_specialization(request, pk, pk2):
    specializations = specialization.objects.get(specialization_id=pk)
    specializations.delete()
    messages.success(request, 'Delete Specialization')
    return redirect('edit-hospital', pk2)

@csrf_exempt
@login_required(login_url='admin_login')
def delete_service(request, pk, pk2):
    services = service.objects.get(service_id=pk)
    services.delete()
    messages.success(request, 'Delete Service')
    return redirect('edit-hospital', pk2)

@csrf_exempt
@login_required(login_url='admin_login')
def edit_emergency_information(request, pk):

    hospital = Hospital_Information.objects.get(hospital_id=pk)
    form = EditEmergencyForm(instance=hospital)  

    if request.method == 'POST':
        form = EditEmergencyForm(request.POST, request.FILES,
                           instance=hospital)  
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency information added')
            return redirect('emergency')
        else:
            form = EditEmergencyForm()

    context = {'hospital': hospital, 'form': form}
    return render(request, 'hospital_admin/edit-emergency-information.html', context)

@csrf_exempt
@login_required(login_url='admin_login')
def delete_hospital(request, pk):
	hospital = Hospital_Information.objects.get(hospital_id=pk)
	hospital.delete()
	return redirect('hospital-list')


@login_required(login_url='admin_login')
def generate_random_invoice():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#INV-" + string_var
    return string_var

@csrf_exempt
@login_required(login_url='admin_login')
def create_invoice(request, pk):
    user = None
    try:
        if hasattr(request.user, 'is_hospital_admin') and request.user.is_hospital_admin:
            user = Admin_Information.objects.get(user=request.user)
    except Admin_Information.DoesNotExist:
        pass

    patient = Patient.objects.get(patient_id=pk)

    if request.method == 'POST':
        # Old Payment model removed - now using Razorpay integration
        # Payments are handled through Razorpay payment views
        messages.success(request, 'Payment processing now handled through Razorpay integration.')
        return redirect('patient-list')

    context = {'patient': patient,'admin': user}
    return render(request, 'hospital_admin/create-invoice.html', context)


@login_required(login_url='admin_login')
def generate_random_specimen():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#INV-" + string_var
    return string_var

@login_required(login_url='admin-login')
@csrf_exempt
def create_report(request, pk):
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
        try:
            prescription = Prescription.objects.get(prescription_id=pk)
        except Prescription.DoesNotExist:
            messages.error(request, 'Prescription not found.')
            return redirect('mypatient-list')
        patient = Patient.objects.get(patient_id=prescription.patient_id)
        doctor = Doctor_Information.objects.get(doctor_id=prescription.doctor_id)
        tests = Prescription_test.objects.filter(prescription=prescription).filter(test_info_pay_status='Paid')
        test_names = Test_Information.objects.all()  # Get all test names for dropdown
        

        if request.method == 'POST':
            from django.utils import timezone
            from datetime import datetime
            
            # Get form data
            specimen_type = request.POST.get('specimen_type')
            collection_date_str = request.POST.get('collection_date')
            receiving_date_str = request.POST.get('receiving_date')
            delivery_date_str = request.POST.get('delivery_date')
            other_information = request.POST.get('other_information')

            # Get test data from multi-select form
            test_names = request.POST.getlist('test_name[]')
            test_ids = request.POST.getlist('test_id[]')
            results = request.POST.getlist('result[]')
            units = request.POST.getlist('unit[]')
            referred_values = request.POST.getlist('referred_value[]')

            # Convert date strings to datetime objects
            collection_date = None
            receiving_date = None
            delivery_date = None
            
            try:
                if collection_date_str:
                    collection_date = datetime.strptime(collection_date_str, '%Y-%m-%d')
                if receiving_date_str:
                    receiving_date = datetime.strptime(receiving_date_str, '%Y-%m-%d')
                if delivery_date_str:
                    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
            except ValueError:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
                return redirect('create-report', pk=pk)

            # Create report with new model fields
            report = Report.objects.create(
                doctor=doctor,
                patient=patient,
                assigned_technician=lab_workers,
                specimen_type=specimen_type,
                collection_date=collection_date,
                receiving_date=receiving_date,
                delivery_date=delivery_date or timezone.now(),
                other_information=other_information,
                status='processing',
                priority='normal'
            )

            # Combine test data into single fields for the report
            if test_names:
                report.test_name = ', '.join([name for name in test_names if name])
                report.result = ', '.join([result for result in results if result])
                report.unit = ', '.join([unit for unit in units if unit])
                report.referred_value = ', '.join([ref for ref in referred_values if ref])
                report.save()

            # Create specimen entry (single entry since it's a dropdown now)
            if specimen_type:  # Only create if specimen type is selected
                specimens = Specimen(report=report)
                specimens.specimen_type = specimen_type
                specimens.collection_date = collection_date
                specimens.receiving_date = receiving_date
                specimens.save()
                
            # Create test entries for each selected test
            for i in range(len(test_names)):
                if test_names[i]:  # Only create if test name exists
                    tests = Test(report=report)
                    tests.test_name = test_names[i]
                    tests.result = results[i] if i < len(results) else ''
                    tests.unit = units[i] if i < len(units) else ''
                    tests.referred_value = referred_values[i] if i < len(referred_values) else ''
                    tests.save()
            
            # mail
            doctor_name = doctor.name
            doctor_email = doctor.email
            patient_name = patient.name
            patient_email = patient.email
            report_id = report.report_id
            delivery_date = report.delivery_date
            collection_date = collection_date  # Assuming this is a list, we can take the first one for the email
            receiving_date = receiving_date  # Assuming this is a list, we can take the first one for the email
            
            subject = "Report Delivery"

            values = {
                    "doctor_name":doctor_name,
                    "doctor_email":doctor_email,
                    "patient_name":patient_name,
                    "report_id":report_id,
                    "delivery_date":delivery_date,
                }

            html_message = render_to_string('hospital_admin/report-mail-delivery.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')
            
            # Send modern notifications
            try:
                send_report_status_notification(report, 'pending', 'processing')
            except Exception as e:
                print(f"Error sending notification: {e}")

            messages.success(request, f'Report created successfully for {patient.name}! Patient has been notified.')
            return redirect('mypatient-list')

        # Predefined specimen types for dropdown
        specimen_types = [
            'Blood',
            'Urine',
            'Saliva',
            'Sputum',
            'Stool (Feces)',
            'Tissue Biopsy',
            'Cerebrospinal Fluid (CSF)',
            'Semen',
            'Vaginal Swab',
            'Nasal Swab',
            'Throat Swab',
            'Amniotic Fluid',
            'Pleural Fluid',
            'Synovial Fluid (Joint Fluid)',
            'Bone Marrow',
            'Other (Specify)'

        ]
        
        # Convert test_names to JSON for JavaScript usage
        test_names_json = json.dumps([{'test_id': test.test_id, 'test_name': test.test_name} for test in test_names])
        
        context = {
            'prescription': prescription,
            'lab_workers': lab_workers,
            'tests': tests, 
            'test_names': test_names, 
            'test_names_json': test_names_json, 
            'patient_id': patient.patient_id,
            'specimen_types': specimen_types
        }
        return render(request, 'hospital_admin/create-report.html',context)

@csrf_exempt
@login_required(login_url='admin_login')
def add_pharmacist(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        form = PharmacistCreationForm()
     
        if request.method == 'POST':
            form = PharmacistCreationForm(request.POST)
            if form.is_valid():
                # form.save(), commit=False --> don't save to database yet (we have a chance to modify object)
                user = form.save(commit=False)
                user.is_pharmacist = True
                user.save()

                messages.success(request, 'Pharmacist account was created!')

                # After user is created, we can log them in
                #login(request, user)
                return redirect('pharmacist-list')
            else:
                messages.error(request, 'An error has occurred during registration')
    
    context = {'form': form, 'admin': user}
    return render(request, 'hospital_admin/add-pharmacist.html', context)
  
@csrf_exempt
@login_required(login_url='admin_login')
def medicine_list(request):
    if request.user.is_authenticated:
        if request.user.is_pharmacist:
            pharmacist = Pharmacist.objects.get(user=request.user)
            
            # Get search query
            medicine_list, search_query = searchMedicines(request)
            
            # Pagination
            from django.core.paginator import Paginator
            paginator = Paginator(medicine_list, 7)  # Show 7 medicines per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            orders = Order.objects.filter(user=request.user, ordered=False)
            carts = Cart.objects.filter(user=request.user, purchased=False)
            
            context = {
                'medicine': page_obj,  # Use paginated object
                'pharmacist': pharmacist,
                'search_query': search_query,
                'orders': orders,
                'carts': carts,
                'page_obj': page_obj,  # Add page_obj for pagination controls
            }
            return render(request, 'hospital_admin/medicine-list.html', context)
                

@login_required(login_url='admin_login')
def generate_random_medicine_ID():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#M-" + string_var
    return string_var

@csrf_exempt
@login_required(login_url='admin_login')
def add_medicine(request):
    from pharmacy.hsn_utils import auto_fetch_hsn_code
    
    user = None
    pharmacist_ctx = None
    if request.user.is_pharmacist:
        user = Pharmacist.objects.get(user=request.user)
        pharmacist_ctx = user
    elif request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)

    if request.method == 'POST':
        # Get form data with proper validation
        name = request.POST.get('name', '').strip()
        composition = request.POST.get('composition', '').strip()
        hsn_code = request.POST.get('hsn_code', '').strip()
        batch_no = request.POST.get('batch_no', '').strip()
        quantity_str = request.POST.get('quantity', '').strip()
        price_str = request.POST.get('price', '').strip()

        requirement_type = request.POST.get('requirement_type', '')
        category_type = request.POST.get('category_type', '')
        medicine_type = request.POST.get('medicine_type', '')
        description = request.POST.get('description', '').strip()
        featured_image = request.FILES.get('featured_image')
        expiry_date_str = request.POST.get('expiry_date', '').strip()
        
        # Auto-fetch HSN code if not provided
        fetch_hsn = request.POST.get('fetch_hsn', 'on') == 'on'
        
        # Parse expiry_date
        from datetime import datetime
        expiry_date = None
        errors = []  # Initialize error flag first
        
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append('Invalid expiry date format.')

        # Validate required fields
        if not name:
            errors.append('Medicine name is required.')
        
        if not batch_no:
            errors.append('Batch number is required.')
        
        # Validate quantity
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                errors.append('Quantity must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid number.')
            quantity = 0
        
        # Validate price
        try:
            price = float(price_str)
            if price < 0:
                errors.append('Price must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number.')
            price = 0

        # Auto-fetch HSN code if requested and not manually provided
        hsn_info = None
        if fetch_hsn and not hsn_code and name:
            hsn_result = auto_fetch_hsn_code(
                medicine_name=name,
                composition=composition,
                category=category_type
            )
            
            if hsn_result.get('hsn_code'):
                hsn_code = hsn_result['hsn_code']
                hsn_info = {
                    'source': hsn_result.get('source', 'unknown'),
                    'confidence': hsn_result.get('confidence', 'low')
                }
                
                # Add success message for HSN fetch
                if hsn_result.get('source') == 'database':
                    messages.info(request, f'HSN code {hsn_code} auto-filled from database')
                elif hsn_result.get('source') == 'api':
                    messages.info(request, f'HSN code {hsn_code} fetched from external API')
                else:
                    messages.warning(request, f'Default HSN code {hsn_code} assigned - please verify manually')

        # If there are errors, return to form with messages
        if errors:
            for error in errors:
                messages.error(request, error)
            ctx = {
                'admin': user,
                'form_data': {
                    'name': name,
                    'composition': composition,
                    'hsn_code': hsn_code,
                    'batch_no': batch_no,
                    'quantity': quantity_str,
                    'price': price_str,
                    'requirement_type': requirement_type,
                    'category_type': category_type,
                    'medicine_type': medicine_type,
                    'description': description,
                    'expiry_date': expiry_date_str,
                },
                'hsn_info': hsn_info
            }
            if pharmacist_ctx:
                ctx['pharmacist'] = pharmacist_ctx
            return render(request, 'hospital_admin/add-medicine.html', ctx)

        # Generate unique medicine ID
        medicine_id = f"#M-{str(uuid.uuid4())[:8].upper()}"

        try:
            # Create medicine instance with new fields
            medicine = Medicine(
                name=name,
                composition=composition,
                hsn_code=hsn_code,
                batch_no=batch_no,
                quantity=quantity,
                price=price,
                stock_quantity=quantity,  # Set stock_quantity equal to quantity for backward compatibility
                Prescription_reqiuired=requirement_type,
                medicine_category=category_type,
                medicine_type=medicine_type,
                description=description,
                featured_image=featured_image or 'medicines/default.png',
                medicine_id=medicine_id,
                expiry_date=expiry_date
            )
            # Save to database
            medicine.save()
            
            # Success message with HSN info
            success_msg = f'Medicine "{name}" added successfully!'
            if hsn_code:
                success_msg += f' (HSN: {hsn_code})'
            if composition:
                success_msg += f' with composition: {composition[:50]}{"..." if len(composition) > 50 else ""}'
                
            messages.success(request, success_msg)
            return redirect('medicine-list')
            
        except Exception as e:
            messages.error(request, f'Error adding medicine: {str(e)}')
            ctx = {'admin': user, 'hsn_info': hsn_info}
            if pharmacist_ctx:
                ctx['pharmacist'] = pharmacist_ctx
            return render(request, 'hospital_admin/add-medicine.html', ctx)

    ctx = {'admin': user}
    if pharmacist_ctx:
        ctx['pharmacist'] = pharmacist_ctx
    return render(request, 'hospital_admin/add-medicine.html', ctx)

@csrf_exempt
@login_required(login_url='admin_login')
def edit_medicine(request, pk):
    from pharmacy.hsn_utils import auto_fetch_hsn_code
    
    if request.user.is_pharmacist:
        user = Pharmacist.objects.get(user=request.user)
        pharmacist_ctx = user
        admin_ctx = None
    elif request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        admin_ctx = user
        pharmacist_ctx = None
    
    medicine = get_object_or_404(Medicine, serial_number=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        
        if form.is_valid():
            updated_medicine = form.save(commit=False)
            
            # Handle HSN auto-fetch if requested
            fetch_hsn = request.POST.get('fetch_hsn', 'off') == 'on'
            if fetch_hsn and not updated_medicine.hsn_code:
                hsn_result = auto_fetch_hsn_code(
                    medicine_name=updated_medicine.name,
                    composition=updated_medicine.composition,
                    category=updated_medicine.medicine_category
                )
                
                if hsn_result.get('hsn_code'):
                    updated_medicine.hsn_code = hsn_result['hsn_code']
                    
                    # Show HSN fetch info
                    if hsn_result.get('source') == 'database':
                        messages.info(request, f'HSN code {hsn_result["hsn_code"]} auto-filled from database')
                    elif hsn_result.get('source') == 'api':
                        messages.info(request, f'HSN code {hsn_result["hsn_code"]} fetched from external API')
                    else:
                        messages.warning(request, f'Default HSN code {hsn_result["hsn_code"]} assigned - please verify manually')
            
            # Handle stock quantity properly
            if 'stock_quantity' in request.POST and request.POST['stock_quantity']:
                try:
                    updated_medicine.stock_quantity = int(request.POST['stock_quantity'])
                except ValueError:
                    pass  # Keep existing value if conversion fails
            
            updated_medicine.save()
            
            # Enhanced success message with composition and HSN info
            success_msg = f'Medicine "{updated_medicine.name}" updated successfully!'
            if updated_medicine.composition:
                success_msg += f' (Composition: {updated_medicine.composition[:50]}{"..." if len(updated_medicine.composition) > 50 else ""})'
            if updated_medicine.hsn_code:
                success_msg += f' [HSN: {updated_medicine.hsn_code}]'
                
            messages.success(request, success_msg)
            return redirect('medicine-list')
        else:
            # Show specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f'Form error: {error}')
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = MedicineForm(instance=medicine)

    context = {
        'form': form, 
        'medicine': medicine, 
        'admin': admin_ctx,
        'pharmacist': pharmacist_ctx,
        'is_edit': True,  # Flag to indicate this is an edit operation
        'form_data': {
            'name': medicine.name,
            'composition': medicine.composition,
            'hsn_code': medicine.hsn_code,
            'weight': medicine.weight,
            'quantity': medicine.quantity,
            'stock_quantity': medicine.stock_quantity,
            'price': medicine.price,
            'requirement_type': medicine.Prescription_reqiuired,
            'category_type': medicine.medicine_category,
            'medicine_type': medicine.medicine_type,
            'description': medicine.description,
            'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d') if medicine.expiry_date else '',
        }
    }
    
    return render(request, 'hospital_admin/edit-medicine.html', context)


@csrf_exempt
@login_required(login_url='admin_login')
def delete_medicine(request, pk):
    if request.user.is_pharmacist:
        user = Pharmacist.objects.get(user=request.user)
        medicine = Medicine.objects.get(serial_number=pk)
        medicine.delete()
        return redirect('medicine-list')

@csrf_exempt
@login_required(login_url='admin_login')
def add_lab_worker(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        
        form = LabWorkerCreationForm()
     
        if request.method == 'POST':
            form = LabWorkerCreationForm(request.POST)
            if form.is_valid():
                try:
                    # form.save(), commit=False --> don't save to database yet (we have a chance to modify object)
                    new_user = form.save(commit=False)
                    new_user.is_labworker = True
                    new_user.save()

                    # Verify that Clinical_Laboratory_Technician was created
                    try:
                        lab_tech = Clinical_Laboratory_Technician.objects.get(user=new_user)
                        messages.success(request, f'Clinical Laboratory Technician account created successfully! Username: {new_user.username}')
                        return redirect('lab-worker-list')
                    except Clinical_Laboratory_Technician.DoesNotExist:
                        new_user.delete()  # Clean up if profile creation failed
                        messages.error(request, 'Error creating lab technician profile. Please contact system administrator.')
                        
                except Exception as e:
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                # Show specific form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f'Form Error: {error}')
                        else:
                            field_name = field.replace('_', ' ').title()
                            messages.error(request, f'{field_name}: {error}')
    
    context = {'form': form, 'admin': user}
    return render(request, 'hospital_admin/add-lab-worker.html', context)  

@csrf_exempt
@login_required(login_url='admin_login')
def view_lab_worker(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        lab_workers = Clinical_Laboratory_Technician.objects.all()
        
    return render(request, 'hospital_admin/lab-worker-list.html', {'lab_workers': lab_workers, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def view_pharmacist(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        pharmcists = Pharmacist.objects.all()
        
    return render(request, 'hospital_admin/pharmacist-list.html', {'pharmacist': pharmcists, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def edit_lab_worker(request, pk):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        lab_worker = Clinical_Laboratory_Technician.objects.get(technician_id=pk)
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = "technician/user-default.png"
                
            name = request.POST.get('name')
            email = request.POST.get('email')     
            phone_number = request.POST.get('phone_number')
            age = request.POST.get('age')  
    
            lab_worker.name = name
            lab_worker.email = email
            lab_worker.phone_number = phone_number
            lab_worker.age = age
            lab_worker.featured_image = featured_image
    
            lab_worker.save()
            
            messages.success(request, 'Clinical Laboratory Technician account updated!')
            return redirect('lab-worker-list')
        
    return render(request, 'hospital_admin/edit-lab-worker.html', {'lab_worker': lab_worker, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def edit_pharmacist(request, pk):
    pharmacist = get_object_or_404(Pharmacist, pharmacist_id=pk)
    admin_ctx = None
    # Allow hospital admin OR the pharmacist owner
    if request.user.is_hospital_admin:
        admin_ctx = Admin_Information.objects.get(user=request.user)
    elif request.user.is_pharmacist and getattr(request.user, 'pharmacist', None) and request.user.pharmacist.pharmacist_id == pharmacist.pharmacist_id:
        # Self-edit allowed
        pass
    else:
        return redirect('admin-logout')

    if request.method == 'POST':
        featured_image = request.FILES.get('featured_image', pharmacist.featured_image or "technician/user-default.png")
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        age = request.POST.get('age')

        pharmacist.name = name
        pharmacist.email = email
        pharmacist.phone_number = phone_number
        pharmacist.age = age
        pharmacist.featured_image = featured_image
        pharmacist.save()
        messages.success(request, 'Pharmacist updated!')
        # Redirect based on role
        if request.user.is_hospital_admin:
            return redirect('pharmacist-list')
        return redirect('pharmacist-dashboard')

    ctx = {'pharmacist': pharmacist}
    if admin_ctx:
        ctx['admin'] = admin_ctx
    return render(request, 'hospital_admin/edit-pharmacist.html', ctx)

@csrf_exempt
@login_required(login_url='admin_login')
def department_image_list(request,pk):
    departments = hospital_department.objects.filter(hospital_id=pk)
    #departments = hospital_department.objects.all()
    context = {'departments': departments}
    return render(request, 'hospital_admin/department-image-list.html',context)

@csrf_exempt
@login_required(login_url='admin_login')
def register_doctor_list(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
        doctors = Doctor_Information.objects.filter(register_status='Accepted')
    return render(request, 'hospital_admin/register-doctor-list.html', {'doctors': doctors, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def pending_doctor_list(request):
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
    doctors = Doctor_Information.objects.filter(register_status='Pending')
    return render(request, 'hospital_admin/Pending-doctor-list.html', {'all': doctors, 'admin': user})

@csrf_exempt
@login_required(login_url='admin_login')
def admin_doctor_profile(request,pk):
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    admin = Admin_Information.objects.get(user=request.user)
    experience= Experience.objects.filter(doctor_id=pk).order_by('-from_year','-to_year')
    education = Education.objects.filter(doctor_id=pk).order_by('-year_of_completion')
    
    context = {'doctor': doctor, 'admin': admin, 'experiences': experience, 'educations': education}
    return render(request, 'hospital_admin/doctor-profile.html',context)


@csrf_exempt
@login_required(login_url='admin_login')
def accept_doctor(request,pk):
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    doctor.register_status = 'Accepted'
    doctor.save()
    
    experience= Experience.objects.filter(doctor_id=pk)
    education = Education.objects.filter(doctor_id=pk)
    
    # Mailtrap
    doctor_name = doctor.name
    doctor_email = doctor.email
    doctor_department = doctor.department_name.hospital_department_name

    doctor_specialization = doctor.specialization.specialization_name

    subject = "Acceptance of Doctor Registration"

    values = {
            "doctor_name":doctor_name,
            "doctor_email":doctor_email,
            "doctor_department":doctor_department,

            "doctor_specialization":doctor_specialization,
        }

    html_message = render_to_string('hospital_admin/accept-doctor-mail.html', {'values': values})
    plain_message = strip_tags(html_message)

    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [doctor_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')

    messages.success(request, 'Doctor Accepted!')
    return redirect('register-doctor-list')


@csrf_exempt
@login_required(login_url='admin_login')
def reject_doctor(request,pk):
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    doctor.register_status = 'Rejected'
    doctor.save()
    
    # Mailtrap
    doctor_name = doctor.name
    doctor_email = doctor.email
    doctor_department = doctor.department_name.hospital_department_name
    doctor_hospital = doctor.hospital_name.name
    doctor_specialization = doctor.specialization.specialization_name

    subject = "Rejection of Doctor Registration"

    values = {
            "doctor_name":doctor_name,
            "doctor_email":doctor_email,
            "doctor_department":doctor_department,
            "doctor_hospital":doctor_hospital,
            "doctor_specialization":doctor_specialization,
        }

    html_message = render_to_string('hospital_admin/reject-doctor-mail.html', {'values': values})
    plain_message = strip_tags(html_message)

    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [doctor_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')
    
    messages.success(request, 'Doctor Rejected!')
    return redirect('register-doctor-list')

@csrf_exempt
@login_required(login_url='admin_login')
def delete_department(request,pk):
    if request.user.is_authenticated:
        if request.user.is_hospital_admin:
            department = hospital_department.objects.get(hospital_department_id=pk)
            department.delete()
            messages.success(request, 'Department Deleted!')
            return redirect('hospital-list')

@login_required(login_url='admin_login')
@csrf_exempt
def edit_department(request,pk):
    if request.user.is_authenticated:
        if request.user.is_hospital_admin:
            # old_featured_image = department.featured_image
            department = hospital_department.objects.get(hospital_department_id=pk)
            old_featured_image = department.featured_image

            if request.method == 'POST':
                if 'featured_image' in request.FILES:
                    featured_image = request.FILES['featured_image']
                else:
                    featured_image = old_featured_image

                department_name = request.POST.get('department_name')
                department.hospital_department_name = department_name
                department.featured_image = featured_image
                department.save()
                messages.success(request, 'Department Updated!')
                return redirect('hospital-list')
                
            context = {'department': department}
            return render(request, 'hospital_admin/edit-hospital.html',context)

@csrf_exempt
@login_required(login_url='admin_login')
def labworker_dashboard(request):
    """Old labworker dashboard - redirects to new comprehensive lab dashboard"""
    if request.user.is_authenticated:
        if request.user.is_labworker:
            # Check if the lab worker is also an admin and redirect to admin dashboard
            if request.user.is_hospital_admin:
                return redirect('admin-dashboard')
            
            # Redirect to new comprehensive lab dashboard
            return redirect('lab-dashboard')
    
    return redirect('admin-login')

@csrf_exempt
@login_required(login_url='admin-login')
def mypatient_list(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            
            # Get filter parameter
            show_filter = request.GET.get('show', 'all')
            
            # Get all prescribed tests with patient information (most recent first)
            all_tests = Prescription_test.objects.select_related(
                'prescription',
                'prescription__patient',
                'prescription__patient__user',
                'prescription__doctor'
            ).filter(
                test_info_pay_status__in=['paid', 'cod_pending', 'cod']  # Show paid, COD pending, and COD tests
            ).order_by('-test_id')
            
            # Count statistics first
            stats = {
                'all': all_tests.count(),
                'pending': all_tests.filter(test_status__in=['paid', 'prescribed']).count(),
                'processing': all_tests.filter(test_status__in=['collected', 'processing']).count(),
                'completed': all_tests.filter(test_status='completed').count(),
            }
            
            # Filter based on status
            if show_filter == 'completed':
                # Show only completed tests
                all_tests = all_tests.filter(test_status='completed')
            elif show_filter == 'processing':
                # Show tests currently being processed
                all_tests = all_tests.filter(test_status__in=['collected', 'processing'])
            elif show_filter == 'pending':
                # Show tests that need action (paid but not yet collected)
                all_tests = all_tests.filter(test_status__in=['paid', 'prescribed'])
            
            # Add additional info to each test
            tests_with_info = []
            for test in all_tests:
                # Get patient information
                if test.prescription and test.prescription.patient:
                    patient = test.prescription.patient
                    test.patient_name = f"{patient.user.first_name} {patient.user.last_name}".strip() or patient.user.username
                    test.patient_phone = getattr(patient, 'phone_number', 'N/A')
                    test.patient_email = getattr(patient, 'email', patient.user.email)
                    test.patient_id = patient.patient_id
                    test.patient_image = patient.featured_image if hasattr(patient, 'featured_image') else None
                    
                    # Get doctor information
                    test.doctor_name = test.prescription.doctor.name if test.prescription.doctor else 'Unknown'
                else:
                    # Handle cases where prescription might be None (standalone tests from before the fix)
                    test.patient_name = 'Standalone Booking'
                    test.patient_phone = 'N/A'
                    test.patient_email = 'N/A' 
                    test.patient_id = 'N/A'
                    test.patient_image = None
                    test.doctor_name = 'Self-Booked'
                    patient = None
                    
                # Check if there's an existing report (only for tests with patients)
                if patient:
                    try:
                        test.report = Report.objects.get(
                            patient=patient,
                            test_name=test.test_name
                        )
                        test.has_report = True
                        test.has_pdf = bool(test.report.file) if hasattr(test.report, 'file') else False
                    except Report.DoesNotExist:
                        test.report = None
                        test.has_report = False
                        test.has_pdf = False
                else:
                    # No patient linked, no report possible
                    test.report = None
                    test.has_report = False
                    test.has_pdf = False
                    
                # Set action buttons availability
                test.can_collect = test.test_status in ['prescribed', 'paid'] and test.test_info_pay_status in ['paid', 'cod_pending', 'cod']
                test.can_process = test.test_status == 'collected'
                test.can_complete = test.test_status == 'processing'
                test.can_upload_result = test.test_status == 'completed'
                test.can_create_report = test.test_status == 'completed' and not test.has_report and patient is not None
                test.can_resubmit_report = test.test_status == 'completed' and test.has_report and patient is not None
                # PDF upload logic: show upload if no PDF, show reupload if PDF exists
                test.show_upload_pdf = test.test_status == 'completed' and not test.has_pdf
                test.show_reupload_pdf = test.test_status == 'completed' and test.has_pdf
                
                tests_with_info.append(test)
            
            context = {
                'tests': tests_with_info,
                'lab_workers': lab_workers,
                'show_filter': show_filter,
                'stats': stats,
                'total_tests': len(tests_with_info)
            }
            return render(request, 'hospital_admin/mypatient-list.html', context)

@csrf_exempt
@login_required(login_url='admin-login')
def prescription_list(request,pk):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            patient = Patient.objects.get(patient_id=pk)
            prescription = Prescription.objects.filter(patient=patient)
            context = {'prescription': prescription,'lab_workers':lab_workers,'patient':patient}
            return render(request, 'hospital_admin/prescription-list.html',context)

@csrf_exempt
@login_required(login_url='admin-login')
def add_test(request):
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)

    if request.method == 'POST':
        tests=Test_Information()
        test_name = request.POST['test_name']
        test_price = request.POST['test_price']
        tests.test_name = test_name
        tests.test_price = test_price

        tests.save()

        return redirect('test-list')
        
    # Get all test names for the dropdown
    test_names = Test_Information.objects.all()
    context = {'lab_workers': lab_workers, 'test_names': test_names}
    return render(request, 'hospital_admin/add-test.html', context)

@csrf_exempt
@login_required(login_url='admin-login')
def test_list(request):
    context = {}
    if request.user.is_labworker:
        try:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            test = Test_Information.objects.all()
            context = {'test':test,'lab_workers':lab_workers}
        except Clinical_Laboratory_Technician.DoesNotExist:
            test = Test_Information.objects.all()
            context = {'test':test,'lab_workers':None}
    else:
        # For non-lab workers, still show tests but without lab worker context
        test = Test_Information.objects.all()
        context = {'test':test,'lab_workers':None}
    return render(request, 'hospital_admin/test-list.html',context)


@csrf_exempt
@login_required(login_url='admin-login')
def delete_test(request,pk):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            test = Test_Information.objects.get(test_id=pk)
            test.delete()
            return redirect('test-list')

@csrf_exempt
def pharmacist_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_pharmacist:
            pharmacist = Pharmacist.objects.get(user=request.user)
            total_pharmacist_count = Pharmacist.objects.annotate(count=Count('pharmacist_id'))
            total_medicine_count = Medicine.objects.annotate(count=Count('serial_number'))
            total_order_count = Order.objects.annotate(count=Count('orderitems'))
            total_cart_count = Cart.objects.annotate(count=Count('item'))

            # Inventory levels based on sellable quantity
            low_stock_count = Medicine.objects.filter(quantity__lt=15).count()
            medium_stock_count = Medicine.objects.filter(quantity__gte=15, quantity__lte=100).count()
            high_stock_count = Medicine.objects.filter(quantity__gt=100).count()
            
            inventory_data = {
                'low_stock': low_stock_count,
                'medium_stock': medium_stock_count,
                'high_stock': high_stock_count
            }

            # Expiring medicines within next 30 days
            import datetime as _dt
            today = _dt.date.today()
            threshold = today + _dt.timedelta(days=30)
            expiring_medicines = Medicine.objects.filter(expiry_date__isnull=False, expiry_date__lte=threshold).order_by('expiry_date')[:20]

            # Sales summaries (today, last 7 days, last 30 days)
            start_today = _dt.datetime.combine(today, _dt.time.min).replace(tzinfo=timezone.get_current_timezone())
            start_7d = start_today - _dt.timedelta(days=7)
            start_30d = start_today - _dt.timedelta(days=30)

            def sum_orders_since(start_dt):
                orders = Order.objects.filter(ordered=True, created__gte=start_dt)
                total = 0.0
                for o in orders:
                    total += float(o.get_totals())
                return round(total, 2)

            sales_today = sum_orders_since(start_today)
            sales_7d = sum_orders_since(start_7d)
            sales_30d = sum_orders_since(start_30d)

            # Top-selling medicines by purchased cart items
            top_selling = (
                Cart.objects.filter(purchased=True)
                .values('item__name')
                .annotate(total_qty=Sum('quantity'))
                .order_by('-total_qty')[:10]
            )

            # Pagination for medicine list
            from django.core.paginator import Paginator
            medicine_list = Medicine.objects.all()
            paginator = Paginator(medicine_list, 7)  # Show 7 medicines per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            # Prepare JSON data for JavaScript charts and search
            import json
            medicines_for_chart = Medicine.objects.all()[:20]  # Top 20 for chart
            all_medicines_for_search = Medicine.objects.all()  # All medicines for search functionality
            
            # Chart data (limited to 20)
            chart_json = json.dumps([
                {
                    'name': medicine.name,
                    'stock': medicine.quantity if medicine.quantity else 0,
                }
                for medicine in medicines_for_chart
            ])
            
            # All medicines data for search and modal functionality
            medicines_json = json.dumps([
                {
                    'id': medicine.serial_number,
                    'serial_number': medicine.serial_number,
                    'name': medicine.name,
                    'stock': medicine.quantity if medicine.quantity else 0,
                    'price': float(medicine.price) if medicine.price else 0.0,
                    'category': medicine.medicine_category or '',
                    'type': medicine.medicine_type or '',
                    'composition': medicine.composition or '',
                    'hsn_code': medicine.hsn_code or ''
                }
                for medicine in all_medicines_for_search
            ])
            
            context = {'pharmacist':pharmacist, 'medicine':page_obj,
                       'medicines': medicine_list,  # All medicines for template
                       'medicines_json': medicines_json,  # All medicines data for search/modal
                       'chart_json': chart_json,  # Limited data for charts
                       'total_pharmacist_count':total_pharmacist_count, 
                       'total_medicine_count':total_medicine_count, 
                       'total_order_count':total_order_count,
                       'total_cart_count':total_cart_count,
                       'inventory_data': inventory_data,
                       'expiring_medicines': expiring_medicines,
                       'sales_today': sales_today,
                       'sales_7d': sales_7d,
                       'sales_30d': sales_30d,
                       'top_selling': top_selling,
                       }
            return render(request, 'hospital_admin/pharmacist-dashboard.html',context)

@csrf_exempt
@login_required(login_url='admin_login')
def increase_medicine_stock(request, pk):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    medicine = get_object_or_404(Medicine, serial_number=pk)
    if request.method == 'POST':
        try:
            count = int(request.POST.get('count', 1))
            if count < 1:
                count = 1
            medicine.quantity = (medicine.quantity or 0) + count
            medicine.stock_quantity = (medicine.stock_quantity or 0) + count
            medicine.save()
            messages.success(request, f"Increased stock for {medicine.name} by {count}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return redirect('pharmacist-dashboard')

@csrf_exempt
@login_required(login_url='admin_login')
def decrease_medicine_stock(request, pk):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    medicine = get_object_or_404(Medicine, serial_number=pk)
    if request.method == 'POST':
        try:
            count = int(request.POST.get('count', 1))
            if count < 1:
                count = 1
            new_q = max(0, (medicine.quantity or 0) - count)
            diff = (medicine.quantity or 0) - new_q
            medicine.quantity = new_q
            medicine.stock_quantity = max(0, (medicine.stock_quantity or 0) - diff)
            medicine.save()
            messages.success(request, f"Decreased stock for {medicine.name} by {diff}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return redirect('pharmacist-dashboard')

@csrf_exempt
def report_history(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:

            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            report = Report.objects.all()
            context = {'report':report,'lab_workers':lab_workers}
            return render(request, 'hospital_admin/report-list.html',context)

@csrf_exempt
@login_required(login_url='admin_login')
def specimen_count_data(request):
    """Return JSON data with specimen type counts for chart visualization"""
    if request.user.is_labworker:
        # Get all distinct specimen types from the database
        specimen_types = Specimen.objects.values_list('specimen_type', flat=True).distinct().order_by('specimen_type')
        
        # Get limit parameter from request to limit number of bars shown
        try:
            limit = int(request.GET.get('limit', 8))
        except ValueError:
            limit = 8
        
        # Get offset parameter for pagination
        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            offset = 0
        
        # Get paginated specimen types
        paginated_specimen_types = list(specimen_types[offset:offset + limit])
        
        # Aggregate specimen counts for the paginated types
        specimen_counts = Specimen.objects.filter(specimen_type__in=paginated_specimen_types).values('specimen_type').annotate(
            count=Count('specimen_type')
        )
        
        # Create a dictionary of counts for the paginated specimen types
        count_dict = {item['specimen_type']: item['count'] for item in specimen_counts}
        
        # Create a list of labels and counts for the chart (ensuring all paginated types are included)
        labels = paginated_specimen_types
        counts = [count_dict.get(spec_type, 0) for spec_type in paginated_specimen_types]
        
        return JsonResponse({'labels': labels, 'counts': counts, 'total_types': len(specimen_types)})

@csrf_exempt
@login_required(login_url='admin_login')
def pharmacist_sales(request):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    pharmacist = Pharmacist.objects.get(user=request.user)

    # Completed orders
    orders = Order.objects.filter(ordered=True).select_related('user').order_by('-created')

    # Optional date filter
    start = request.GET.get('start')
    end = request.GET.get('end')
    from datetime import datetime as _dt
    if start:
        try:
            start_dt = _dt.strptime(start, "%Y-%m-%d")
            orders = orders.filter(created__date__gte=start_dt.date())
        except ValueError:
            messages.error(request, 'Invalid start date')
    if end:
        try:
            end_dt = _dt.strptime(end, "%Y-%m-%d")
            orders = orders.filter(created__date__lte=end_dt.date())
        except ValueError:
            messages.error(request, 'Invalid end date')

    # Aggregate totals
    total_revenue = sum(float(o.get_totals()) for o in orders)
    total_orders = orders.count()

    # Top 10 items by quantity within filtered orders timeframe/users
    carts_qs = Cart.objects.filter(purchased=True)
    user_ids = list(orders.values_list('user_id', flat=True))
    if user_ids:
        carts_qs = carts_qs.filter(user_id__in=user_ids)
    if start:
        try:
            carts_qs = carts_qs.filter(updated__date__gte=start_dt.date())
        except Exception:
            pass
    if end:
        try:
            carts_qs = carts_qs.filter(updated__date__lte=end_dt.date())
        except Exception:
            pass
    top_items = carts_qs.values('item__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:10]

    context = {
        'orders': orders,
        'total_revenue': round(total_revenue, 2),
        'total_orders': total_orders,
        'top_items': top_items,
        'start': start or '',
        'end': end or '',
        'pharmacist': pharmacist,
    }
    return render(request, 'hospital_admin/pharmacist-sales.html', context)


@csrf_exempt
@login_required(login_url='admin_login')
def pharmacist_purchase_history(request):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    pharmacist = Pharmacist.objects.get(user=request.user)

    # Get completed orders with their items (including COD orders)
    from pharmacy.models import Order
    from django.db.models import Q
    completed_orders = (
        Order.objects.filter(ordered=True)
        .filter(Q(payment_status='paid') | Q(payment_status='cod') | Q(payment_status='cash_on_delivery'))
        .select_related('user')
        .prefetch_related('orderitems__item')
        .order_by('-created')
    )

    # Each purchased cart item as row history (for backward compatibility)
    purchased_items = (
        Cart.objects.filter(purchased=True)
        .select_related('item', 'user')
        .order_by('-updated')
    )

    context = {
        'purchased_items': purchased_items,
        'completed_orders': completed_orders,
        'pharmacist': pharmacist,
    }
    return render(request, 'hospital_admin/pharmacist-purchase-history.html', context)


@csrf_exempt
@login_required(login_url='admin_login')
def pharmacist_order_management(request):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    pharmacist = Pharmacist.objects.get(user=request.user)

    # Get all orders with different payment statuses
    from pharmacy.models import Order, PrescriptionUpload
    from django.db.models import Q
    
    # Online paid orders
    online_orders = (
        Order.objects.filter(ordered=True, payment_status='paid')
        .exclude(order_status__in=['delivered', 'completed', 'cancelled'])
        .select_related('user__patient')
        .prefetch_related('orderitems__item')
        .order_by('-created')
    )
    
    # COD orders (Cash on Delivery)
    cod_orders = (
        Order.objects.filter(
            ordered=True, 
            payment_status__in=['cod', 'cash_on_delivery', 'cod_pending']
        )
        .exclude(order_status__in=['delivered', 'completed', 'cancelled'])
        .select_related('user__patient')
        .prefetch_related('orderitems__item')
        .order_by('-created')
    )
    
    # Failed payment orders that need attention
    failed_orders = (
        Order.objects.filter(
            Q(payment_status='failed') | Q(payment_status='pending'),
            ordered=False
        )
        .select_related('user__patient')
        .prefetch_related('orderitems__item')
        .order_by('-created')[:10]  # Last 10 failed orders
    )
    
    # Orders ready for pickup
    ready_orders = (
        Order.objects.filter(
            ordered=True,
            order_status='ready',
            payment_status__in=['paid', 'cod', 'cash_on_delivery']
        )
        .select_related('user__patient')
        .prefetch_related('orderitems__item')
        .order_by('created')
    )
    
    # Out for delivery orders
    delivery_orders = (
        Order.objects.filter(
            ordered=True,
            order_status='out_for_delivery',
            delivery_method='delivery'
        )
        .select_related('user__patient')
        .prefetch_related('orderitems__item')
        .order_by('created')
    )

    # Calculate stats
    total_pending = online_orders.count() + cod_orders.count()
    total_revenue_today = sum([
        float(order.final_bill()) for order in 
        Order.objects.filter(
            ordered=True,
            payment_status__in=['paid', 'cod', 'cash_on_delivery'],
            created__date=timezone.now().date()
        )
    ])
    
    # Low stock medicines alert
    low_stock_medicines = Medicine.objects.filter(quantity__lte=10).order_by('quantity')[:10]

    # PRESCRIPTION UPLOADS MANAGEMENT
    # Pending prescription reviews
    pending_prescriptions = (
        PrescriptionUpload.objects.filter(status='pending')
        .select_related('patient')
        .order_by('-uploaded_at')
    )
    
    # Approved prescriptions waiting for payment
    approved_prescriptions = (
        PrescriptionUpload.objects.filter(status='approved', related_order__isnull=True)
        .select_related('patient', 'pharmacist')
        .prefetch_related('medicines__medicine')
        .order_by('-reviewed_at')
    )
    
    # Paid prescriptions waiting for processing (NEW)
    paid_pending_prescriptions = (
        PrescriptionUpload.objects.filter(status='paid_pending')
        .select_related('patient', 'pharmacist', 'related_order')
        .prefetch_related('medicines__medicine')
        .order_by('-updated_at')
    )
    
    # Fulfilled prescription orders
    fulfilled_prescriptions = (
        PrescriptionUpload.objects.filter(status='fulfilled')
        .select_related('patient', 'pharmacist', 'related_order')
        .prefetch_related('medicines__medicine')
        .order_by('-updated_at')[:20]  # Last 20 fulfilled prescriptions
    )
    
    # Rejected prescriptions (for review)
    rejected_prescriptions = (
        PrescriptionUpload.objects.filter(status='rejected')
        .select_related('patient', 'pharmacist')
        .order_by('-reviewed_at')[:10]  # Last 10 rejected
    )

    context = {
        'online_orders': online_orders,
        'cod_orders': cod_orders,
        'failed_orders': failed_orders,
        'ready_orders': ready_orders,
        'delivery_orders': delivery_orders,
        'pharmacist': pharmacist,
        'total_pending': total_pending,
        'total_revenue_today': round(total_revenue_today, 2),
        'low_stock_medicines': low_stock_medicines,
        # Prescription management
        'pending_prescriptions': pending_prescriptions,
        'approved_prescriptions': approved_prescriptions,
        'paid_pending_prescriptions': paid_pending_prescriptions,
        'fulfilled_prescriptions': fulfilled_prescriptions,
        'rejected_prescriptions': rejected_prescriptions,
    }
    return render(request, 'hospital_admin/pharmacist-order-management.html', context)


@csrf_exempt
@login_required(login_url='admin_login')
def update_order_status(request, order_id):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    
    from pharmacy.models import Order
    from django.http import JsonResponse
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('order_status')
        pharmacist_notes = request.POST.get('pharmacist_notes', '')
        payment_collected = request.POST.get('payment_collected', 'no')  # For COD orders
        
        # Get valid status choices
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        
        if new_status in valid_statuses:
            old_status = order.order_status
            order.order_status = new_status
            
            if pharmacist_notes:
                existing_notes = order.pharmacist_notes or ""
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
                order.pharmacist_notes = f"{existing_notes}\n[{timestamp}] {pharmacist_notes}".strip()
            
            # Handle COD payment collection
            if order.payment_status in ['cod', 'cash_on_delivery', 'cod_pending']:
                if payment_collected == 'yes' and new_status in ['delivered', 'completed']:
                    order.payment_status = 'paid'  # Mark as paid when COD is collected
                    success_message = f'Order #{order.id} completed and payment collected'
                elif new_status == 'cancelled':
                    success_message = f'COD Order #{order.id} cancelled'
                else:
                    success_message = f'COD Order #{order.id} status updated to {order.get_order_status_display()}'
            else:
                success_message = f'Order #{order.id} status updated to {order.get_order_status_display()}'
            
            # Stock management for cancelled orders
            if new_status == 'cancelled' and old_status != 'cancelled':
                try:
                    # Restore stock quantities
                    for order_item in order.orderitems.all():
                        medicine = order_item.item
                        medicine.quantity += order_item.quantity
                        if medicine.stock_quantity is not None:
                            medicine.stock_quantity += order_item.quantity
                        medicine.save()
                    success_message += " - Stock quantities restored"
                except Exception as e:
                    success_message += f" - Warning: Stock restoration failed: {str(e)}"
            
            order.save()
            
            # Send notifications if needed
            try:
                send_order_status_notification(order, old_status, new_status)
            except Exception as e:
                # Don't fail the update if notification fails
                pass
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'new_status': order.get_order_status_display(),
                    'payment_status': order.payment_status
                })
            
            messages.success(request, success_message)
        else:
            error_message = 'Invalid order status'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            messages.error(request, error_message)
    
    return redirect('pharmacist-order-management')


def send_order_status_notification(order, old_status, new_status):
    """Send notification when order status changes"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        if not hasattr(order.user, 'patient'):
            return
            
        patient = order.user.patient
        
        # Status change messages
        status_messages = {
            'confirmed': 'Your order has been confirmed and is being prepared.',
            'preparing': 'Your medicines are being prepared by our pharmacist.',
            'ready': 'Your order is ready for pickup at the pharmacy.',
            'out_for_delivery': 'Your order is out for delivery.',
            'delivered': 'Your order has been delivered successfully.',
            'completed': 'Your order has been completed.',
            'cancelled': 'Your order has been cancelled. Any payment will be refunded.'
        }
        
        message = status_messages.get(new_status, f'Your order status has been updated to {new_status}.')
        
        subject = f'Order #{order.id} Status Update - {order.get_order_status_display()}'
        
        email_body = f"""
Dear {patient.name},

{message}

Order Details:
- Order ID: #{order.id}
- Total Amount: ₹{order.final_bill()}
- Payment Status: {order.payment_status}
- Delivery Method: {order.get_delivery_method_display()}

"""
        
        if order.pharmacist_notes:
            email_body += f"\nPharmacist Notes:\n{order.pharmacist_notes}\n"
        
        if new_status == 'ready' and order.delivery_method == 'pickup':
            email_body += "\nPlease visit the pharmacy to collect your medicines.\n"
        elif new_status == 'out_for_delivery':
            email_body += f"\nDelivery Address: {order.delivery_address}\nContact: {order.delivery_phone}\n"
        
        email_body += """
Thank you for choosing Mahima Medicare.

Best regards,
Mahima Medicare Team
"""
        
        send_mail(
            subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [patient.email],
            fail_silently=True
        )
        
    except Exception as e:
        # Log error but don't raise it
        print(f"Error sending order notification: {e}")


@csrf_exempt
@login_required(login_url='admin_login')
def process_cod_payment(request, order_id):
    """Process COD payment collection by pharmacist"""
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    
    from pharmacy.models import Order
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        amount_received = request.POST.get('amount_received', '0')
        payment_notes = request.POST.get('payment_notes', '')
        
        try:
            amount_received = float(amount_received)
            expected_amount = float(order.final_bill())
            
            if amount_received >= expected_amount:
                order.payment_status = 'paid'
                order.order_status = 'completed'
                
                # Add payment collection notes
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
                payment_note = f"[{timestamp}] COD Payment Collected - Amount: ₹{amount_received}"
                if payment_notes:
                    payment_note += f" - Notes: {payment_notes}"
                
                existing_notes = order.pharmacist_notes or ""
                order.pharmacist_notes = f"{existing_notes}\n{payment_note}".strip()
                order.save()
                
                messages.success(request, f'COD payment collected successfully for Order #{order.id}')
            else:
                messages.error(request, f'Insufficient payment. Expected: ₹{expected_amount}, Received: ₹{amount_received}')
        except ValueError:
            messages.error(request, 'Invalid payment amount')
    
    return redirect('pharmacist-order-management')


@csrf_exempt
@login_required(login_url='admin_login')
def handle_payment_failure(request, order_id):
    """Handle failed payment scenarios"""
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    
    from pharmacy.models import Order
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'retry_payment':
            # Reset order for payment retry
            order.payment_status = 'pending'
            order.ordered = False
            order.save()
            messages.success(request, f'Order #{order.id} reset for payment retry')
            
        elif action == 'convert_to_cod':
            # Convert to COD
            order.payment_status = 'cod'
            order.ordered = True
            order.order_status = 'confirmed'
            order.save()
            messages.success(request, f'Order #{order.id} converted to Cash on Delivery')
            
        elif action == 'cancel_order':
            # Cancel the order and restore stock
            try:
                for order_item in order.orderitems.all():
                    medicine = order_item.item
                    medicine.quantity += order_item.quantity
                    if medicine.stock_quantity is not None:
                        medicine.stock_quantity += order_item.quantity
                    medicine.save()
                
                order.order_status = 'cancelled'
                order.payment_status = 'cancelled'
                order.save()
                messages.success(request, f'Order #{order.id} cancelled and stock restored')
            except Exception as e:
                messages.error(request, f'Error cancelling order: {str(e)}')
    
    return redirect('pharmacist-order-management')


@csrf_exempt
@login_required(login_url='admin_login')
def bulk_medicine_management(request):
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    pharmacist = Pharmacist.objects.get(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Bulk delete
        if action == 'delete':
            ids = request.POST.getlist('ids')
            try:
                Medicine.objects.filter(serial_number__in=ids).delete()
                messages.success(request, f"Deleted {len(ids)} medicines.")
            except Exception as e:
                messages.error(request, f"Error deleting: {e}")
            return redirect('bulk-medicine-management')

        # CSV import
        if action == 'import':
            file = request.FILES.get('file')
            if not file:
                messages.error(request, 'No file uploaded')
                return redirect('bulk-medicine-management')

            import csv, io
            try:
                decoded = file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded))
                created = 0
                for row in reader:
                    name = (row.get('name') or '').strip()
                    if not name:
                        continue
                    quantity = int(row.get('quantity') or 0)
                    price = float(row.get('price') or 0)
                    weight = (row.get('weight') or '').strip()
                    description = (row.get('description') or '').strip()
                    composition = (row.get('composition') or '').strip()
                    hsn_code = (row.get('hsn_code') or '').strip()
                    medicine_type = (row.get('medicine_type') or '').strip() or None
                    medicine_category = (row.get('medicine_category') or '').strip() or None
                    requirement = (row.get('prescription_required') or '').strip() or None
                    expiry_date = None
                    exp = (row.get('expiry_date') or '').strip()
                    if exp:
                        try:
                            from datetime import datetime as _dt2
                            expiry_date = _dt2.strptime(exp, '%Y-%m-%d').date()
                        except ValueError:
                            expiry_date = None

                    # Auto-fetch HSN if not provided but composition is available
                    if composition and not hsn_code:
                        from pharmacy.hsn_utils import auto_fetch_hsn_code
                        hsn_result = auto_fetch_hsn_code(name, composition, medicine_category)
                        if hsn_result['success']:
                            hsn_code = hsn_result['hsn_code']

                    Medicine.objects.create(
                        name=name,
                        weight=weight,
                        quantity=quantity,
                        stock_quantity=quantity,
                        price=price,
                        description=description,
                        composition=composition,
                        hsn_code=hsn_code,
                        medicine_type=medicine_type,
                        medicine_category=medicine_category,
                        Prescription_reqiuired=requirement,
                        featured_image='medicines/default.png',
                        medicine_id=f"#M-{str(uuid.uuid4())[:8].upper()}",
                        expiry_date=expiry_date,
                    )
                    created += 1
                messages.success(request, f"Imported {created} medicines from CSV.")
            except Exception as e:
                messages.error(request, f"Import failed: {e}")
            return redirect('bulk-medicine-management')

    medicines = Medicine.objects.all().order_by('name')
    return render(request, 'hospital_admin/bulk-medicine.html', {'medicine_list': medicines, 'pharmacist': pharmacist})


# Lab Report PDF Upload/Download Views
@csrf_exempt
@login_required(login_url='admin_login')
def upload_report_pdf(request, report_id):
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    if request.method == 'POST':
        pdf_file = request.FILES.get('report_pdf')
        if pdf_file:
            # Validate file type
            if not pdf_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Please upload a PDF file only.')
                return redirect('upload-report-pdf', report_id=report_id)
            
            report.report_pdf = pdf_file
            report.save()
            messages.success(request, f'PDF report uploaded successfully for {report.patient.username}')
            return redirect('report-history')
        else:
            messages.error(request, 'Please select a PDF file to upload.')
    
    context = {
        'report': report,
        'lab_workers': lab_worker,
    }
    return render(request, 'hospital_admin/upload-report-pdf.html', context)


@csrf_exempt
@login_required(login_url='admin_login')
def download_report_pdf(request, report_id):
    report = get_object_or_404(Report, report_id=report_id)
    
    # Check permissions - lab worker or patient owner
    if request.user.is_labworker:
        pass  # Lab workers can download any report
    elif hasattr(request.user, 'patient') and request.user.patient == report.patient:
        pass  # Patients can download their own reports
    else:
        messages.error(request, 'You do not have permission to access this report.')
        return redirect('patient-dashboard' if hasattr(request.user, 'patient') else 'labworker-dashboard')
    
    if not report.report_pdf:
        messages.error(request, 'No PDF report available for download.')
        return redirect('patient-dashboard' if hasattr(request.user, 'patient') else 'report-history')
    
    from django.http import FileResponse
    import os
    
    try:
        response = FileResponse(
            report.report_pdf.open('rb'),
            as_attachment=True,
            filename=f'lab_report_{report.report_id}_{report.patient.username}.pdf'
        )
        return response
    except Exception as e:
        messages.error(request, 'Error downloading report. Please try again.')
        return redirect('patient-dashboard' if hasattr(request.user, 'patient') else 'report-history')


@csrf_exempt
@login_required(login_url='admin_login')
def direct_upload_pdf_report(request, patient_id):
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        pdf_file = request.FILES.get('report_pdf')
        test_name = request.POST.get('test_name', '').strip()
        specimen_type = request.POST.get('specimen_type', '').strip()
        collection_date = request.POST.get('collection_date', '').strip()
        delivery_date = request.POST.get('delivery_date', '').strip()
        other_information = request.POST.get('other_information', '').strip()
        
        if pdf_file and test_name:
            # Validate file type
            if not pdf_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Please upload a PDF file only.')
                return redirect('direct-upload-pdf-report', patient_id=patient_id)
            
            # Create new report with PDF and proper status
            from django.utils import timezone
            report = Report.objects.create(
                patient=patient,
                assigned_technician=lab_worker,
                test_name=test_name,
                specimen_type=specimen_type,
                collection_date=collection_date if collection_date else timezone.now(),
                delivery_date=timezone.now(),
                other_information=other_information,
                report_pdf=pdf_file,
                status='completed',  # Mark as completed since PDF is uploaded
                priority='normal'
            )
            
            # Send completion notifications
            try:
                send_report_completion_notification(report)
            except Exception as e:
                print(f"Error sending notification: {e}")
            
            messages.success(request, f'PDF report uploaded successfully for {patient.name}')
            return redirect('mypatient-list')
        else:
            messages.error(request, 'Please provide test name and select a PDF file.')
    
    context = {
        'patient': patient,
        'lab_workers': lab_worker,
    }
    return render(request, 'hospital_admin/direct-upload-pdf-report.html', context)


# ==================== ENHANCED LAB MANAGEMENT VIEWS ====================

@login_required(login_url='admin-login')
def lab_dashboard(request):
    """Comprehensive lab dashboard with complete doctor-patient-lab integration"""
    # Check if user has lab worker permissions
    if not getattr(request.user, 'is_labworker', False) and not request.user.is_staff:
        return redirect('admin-logout')
    
    # Get lab worker profile, create if doesn't exist
    try:
        lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    except Clinical_Laboratory_Technician.DoesNotExist:
        # Create a lab worker profile for this user
        lab_worker = Clinical_Laboratory_Technician.objects.create(
            user=request.user,
            name=f'{request.user.first_name} {request.user.last_name}' or request.user.username,
            username=request.user.username,
            email=request.user.email,
            phone_number=1234567890,
            age=30
        )
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # === TEST STATISTICS ===
    # All prescribed tests with comprehensive data
    all_tests = Prescription_test.objects.select_related(
        'prescription', 'prescription__patient', 'prescription__patient__user',
        'prescription__doctor', 'assigned_technician'
    ).all()
    
    # Test status breakdown
    test_stats = {
        'total_prescribed': all_tests.count(),
        'paid_tests': all_tests.filter(test_info_pay_status='paid').count(),
        'pending_collection': all_tests.filter(test_status__in=['prescribed', 'paid'], test_info_pay_status='paid').count(),
        'collected': all_tests.filter(test_status='collected').count(),
        'processing': all_tests.filter(test_status='processing').count(),
        'completed': all_tests.filter(test_status='completed').count(),
        'unpaid': all_tests.filter(test_info_pay_status='unpaid').count(),
    }
    
    # My workload
    my_assigned_tests = all_tests.filter(assigned_technician=lab_worker)
    completed_today_count = my_assigned_tests.filter(
        test_status='completed',
        updated_at__date=today
    ).count()
    total_assigned_count = my_assigned_tests.count()
    
    my_workload = {
        'total_assigned': total_assigned_count,
        'pending_work': my_assigned_tests.filter(test_status__in=['paid', 'collected']).count(),
        'currently_processing': my_assigned_tests.filter(test_status='processing').count(),
        'completed_today': completed_today_count,
        'completed_week': my_assigned_tests.filter(
            test_status='completed',
            updated_at__date__gte=week_ago
        ).count(),
        'completion_percentage': (completed_today_count / total_assigned_count * 100) if total_assigned_count > 0 else 0,
    }
    
    # === DOCTOR-PATIENT-LAB INTEGRATION ===
    # Recent prescriptions with doctor-patient details
    recent_prescriptions = Prescription.objects.select_related(
        'doctor', 'patient', 'patient__user'
    ).filter(
        prescription_test__test_info_pay_status='paid'
    ).distinct().order_by('-create_date')[:10]
    
    # Add test details to each prescription
    for prescription in recent_prescriptions:
        prescription.tests = Prescription_test.objects.filter(
            prescription=prescription,
            test_info_pay_status='paid'
        ).select_related('assigned_technician')
        
        # Doctor information
        prescription.doctor_info = {
            'name': prescription.doctor.name,
            'department': prescription.doctor.department,
            'specialization': prescription.doctor.specialization.specialization_name if prescription.doctor.specialization else 'General',
        }
        
        # Patient information  
        prescription.patient_info = {
            'name': f"{prescription.patient.user.first_name} {prescription.patient.user.last_name}".strip() or prescription.patient.user.username,
            'age': getattr(prescription.patient, 'age', 'N/A'),
            'phone': getattr(prescription.patient, 'phone_number', 'N/A'),
            'email': prescription.patient.user.email,
        }
    
    # === URGENT WORK QUEUE ===
    urgent_tests = all_tests.filter(
        test_info_pay_status='paid',
        test_status__in=['paid', 'collected', 'processing']
    ).select_related(
        'prescription__doctor', 'prescription__patient__user'
    ).order_by('created_at')[:15]
    
    # Add priority and timing information
    for test in urgent_tests:
        test.doctor_name = test.prescription.doctor.name if test.prescription.doctor else "Unknown Doctor"
        test.patient_name = f"{test.prescription.patient.user.first_name} {test.prescription.patient.user.last_name}".strip() if test.prescription.patient and test.prescription.patient.user else "Unknown Patient"
        
        # Safe date parsing with fallback
        try:
            if test.prescription.create_date:
                prescription_date = timezone.datetime.strptime(test.prescription.create_date, '%Y-%m-%d').date()
                test.days_since_prescription = (timezone.now().date() - prescription_date).days
            else:
                # Fallback: use test creation date if prescription date is missing
                test.days_since_prescription = (timezone.now().date() - test.created_at.date()).days
        except (ValueError, TypeError, AttributeError):
            # Fallback: assume recent if date parsing fails
            test.days_since_prescription = 0
        
        # Determine urgency
        if test.days_since_prescription > 3:
            test.urgency = 'high'
        elif test.days_since_prescription > 1:
            test.urgency = 'medium'
        else:
            test.urgency = 'normal'
    
    # === DOCTOR ACTIVITY ANALYSIS ===
    # Note: Using prescription_test creation date since prescription.create_date is unreliable CharField
    doctor_stats = Prescription.objects.filter(
        prescription_test__test_info_pay_status='paid',
        prescription_test__created_at__gte=(today - timedelta(days=30))
    ).values(
        'doctor__name', 'doctor__department'
    ).annotate(
        total_tests_prescribed=Count('prescription_test'),
        total_patients=Count('patient', distinct=True)
    ).order_by('-total_tests_prescribed')[:10]
    
    # === PERFORMANCE METRICS ===
    performance_metrics = {
        'avg_completion_time': my_assigned_tests.filter(
            test_status='completed',
            updated_at__date__gte=week_ago
        ).count(),  # Simplified for now
        'daily_throughput': my_assigned_tests.filter(
            test_status='completed',
            updated_at__date=today
        ).count(),
        'accuracy_rate': 98.5,  # Placeholder - can be calculated based on QC data
        'patient_satisfaction': 4.7,  # Placeholder - from feedback system
    }
    
    # === RECENT ACTIVITY FEED ===
    recent_activity = []
    
    # Recently completed tests
    completed_today = my_assigned_tests.filter(
        test_status='completed',
        updated_at__date=today
    ).select_related('prescription__patient__user')[:5]
    
    for test in completed_today:
        # Safe patient name extraction
        patient_name = "Unknown Patient"
        if test.prescription and test.prescription.patient and test.prescription.patient.user:
            user = test.prescription.patient.user
            patient_name = f"{user.first_name} {user.last_name}".strip() or user.username or "Unknown Patient"
        
        recent_activity.append({
            'type': 'completion',
            'message': f"Completed {test.test_name or 'Test'} for {patient_name}",
            'time': test.updated_at,
            'icon': 'fa-check-circle',
            'color': 'success'
        })
    
    # Recently assigned tests
    newly_assigned = my_assigned_tests.filter(
        assigned_technician=lab_worker,
        test_status__in=['paid', 'collected']
    ).order_by('-updated_at')[:3]
    
    for test in newly_assigned:
        # Safe patient name extraction
        patient_name = "Unknown Patient"
        if test.prescription and test.prescription.patient and test.prescription.patient.user:
            user = test.prescription.patient.user
            patient_name = f"{user.first_name} {user.last_name}".strip() or user.username or "Unknown Patient"
            
        recent_activity.append({
            'type': 'assignment',
            'message': f"Assigned {test.test_name or 'Test'} for {patient_name}",
            'time': test.updated_at,
            'icon': 'fa-user-check',
            'color': 'info'
        })
    
    # Sort recent activity by time
    recent_activity.sort(key=lambda x: x['time'], reverse=True)
    
    # === COMPREHENSIVE TEST WORKFLOW DATA ===
    # Get all tests with detailed workflow information (like mypatient_list)
    workflow_tests = all_tests.select_related(
        'prescription__patient__user', 'prescription__doctor'
    )[:20]  # Limit to recent 20 tests for dashboard display
    
    tests_with_workflow = []
    for test in workflow_tests:
        if test.prescription and test.prescription.patient:
            patient = test.prescription.patient
            
            # Safe patient name extraction
            if patient.user:
                test.patient_name = f"{patient.user.first_name or ''} {patient.user.last_name or ''}".strip() or patient.user.username or 'Unknown Patient'
                test.patient_email = getattr(patient, 'email', patient.user.email if patient.user.email else 'N/A')
            else:
                test.patient_name = 'Unknown Patient'
                test.patient_email = 'N/A'
                
            test.patient_phone = getattr(patient, 'phone_number', 'N/A')
            test.patient_id = getattr(patient, 'patient_id', 'N/A')
            test.patient_image = getattr(patient, 'featured_image', None)
            
            # Get doctor information safely
            test.doctor_name = test.prescription.doctor.name if test.prescription.doctor else 'Unknown'
            
            # Check if there's an existing report/PDF
            try:
                test.report = Report.objects.get(
                    patient=patient,
                    test_name=test.test_name
                )
                test.has_pdf = bool(getattr(test.report, 'file', None))
                test.has_report = True
            except (Report.DoesNotExist, AttributeError):
                test.report = None
                test.has_pdf = False
                test.has_report = False
            
            # Set action buttons availability
            test.can_collect = test.test_status in ['prescribed', 'paid'] and test.test_info_pay_status == 'paid'
            test.can_process = test.test_status == 'collected'
            test.can_complete = test.test_status == 'processing'
            test.can_create_report = test.test_status == 'completed' and not test.has_report
            test.can_resubmit_report = test.test_status == 'completed' and test.has_report
            # PDF upload logic: show upload if no PDF, show reupload if PDF exists
            test.show_upload_pdf = test.test_status == 'completed' and not test.has_pdf
            test.show_reupload_pdf = test.test_status == 'completed' and test.has_pdf
            
            tests_with_workflow.append(test)
    
    context = {
        'lab_worker': lab_worker,
        'test_stats': test_stats,
        'my_workload': my_workload,
        'recent_prescriptions': recent_prescriptions,
        'urgent_tests': urgent_tests,
        'doctor_stats': doctor_stats,
        'performance_metrics': performance_metrics,
        'recent_activity': recent_activity[:10],
        'tests_with_workflow': tests_with_workflow,  # Add workflow test data
        'today': today,
    }
    
    return render(request, 'hospital_admin/lab-dashboard.html', context)


@login_required(login_url='admin-login')
def lab_dashboard_simple(request):
    """Simple, reliable lab dashboard with basic functionality"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Basic test statistics with error handling
    try:
        all_tests = Prescription_test.objects.select_related(
            'prescription', 'prescription__patient', 'prescription__patient__user',
            'prescription__doctor', 'assigned_technician'
        ).all()
        
        test_stats = {
            'total_prescribed': all_tests.count(),
            'pending_collection': all_tests.filter(
                test_status__in=['prescribed', 'paid'], 
                test_info_pay_status='paid'
            ).count(),
            'processing': all_tests.filter(test_status='processing').count(),
            'completed': all_tests.filter(test_status='completed').count(),
        }
        
        # My workload with safe calculations
        my_assigned_tests = all_tests.filter(assigned_technician=lab_worker)
        completed_today_count = my_assigned_tests.filter(
            test_status='completed',
            updated_at__date=today
        ).count()
        total_assigned_count = my_assigned_tests.count()
        
        my_workload = {
            'total_assigned': total_assigned_count,
            'completed_today': completed_today_count,
            'completed_week': my_assigned_tests.filter(
                test_status='completed',
                updated_at__date__gte=week_ago
            ).count(),
            'completion_percentage': (completed_today_count / total_assigned_count * 100) if total_assigned_count > 0 else 0,
        }
        
        # Performance metrics
        performance_metrics = {
            'daily_throughput': completed_today_count,
        }
        
        # Recent activity (simplified)
        recent_activity = []
        completed_today = my_assigned_tests.filter(
            test_status='completed',
            updated_at__date=today
        ).select_related('prescription__patient__user')[:5]
        
        for test in completed_today:
            patient_name = f"{test.prescription.patient.user.first_name} {test.prescription.patient.user.last_name}".strip()
            if not patient_name:
                patient_name = test.prescription.patient.user.username
            
            recent_activity.append({
                'type': 'completion',
                'message': f"Completed {test.test_name} for {patient_name}",
                'time': test.updated_at,
                'icon': 'fa-check-circle',
                'color': 'success'
            })
        
    except Exception as e:
        # Fallback data if database issues
        test_stats = {
            'total_prescribed': 0,
            'pending_collection': 0,
            'processing': 0,
            'completed': 0,
        }
        my_workload = None
        performance_metrics = {'daily_throughput': 0}
        recent_activity = []
    
    context = {
        'lab_worker': lab_worker,
        'test_stats': test_stats,
        'my_workload': my_workload,
        'performance_metrics': performance_metrics,
        'recent_activity': recent_activity,
        'today': today,
    }
    
    return render(request, 'hospital_admin/lab-dashboard-simple.html', context)


@login_required(login_url='admin-login')
def lab_report_queue(request):
    """View all reports in queue with filtering and assignment options"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    assigned_filter = request.GET.get('assigned', 'all')
    
    # Base queryset
    reports = Report.objects.all().order_by('-uploaded_at')
    
    # Apply filters
    if status_filter != 'all':
        reports = reports.filter(status=status_filter)
    
    if priority_filter != 'all':
        reports = reports.filter(priority=priority_filter)
    
    if assigned_filter == 'me':
        reports = reports.filter(assigned_technician=lab_worker)
    elif assigned_filter == 'unassigned':
        reports = reports.filter(assigned_technician__isnull=True)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'lab_worker': lab_worker,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_filter': assigned_filter,
        'status_choices': Report.REPORT_STATUS_CHOICES,
        'priority_choices': Report.PRIORITY_CHOICES,
    }
    
    return render(request, 'hospital_admin/lab-report-queue.html', context)


@login_required(login_url='admin-login')
def assign_report_to_me(request, report_id):
    """Assign a report to the current lab technician"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    if report.assigned_technician is None:
        report.assigned_technician = lab_worker
        report.status = 'collected'
        report.save()
        
        messages.success(request, f'Report #{report.report_id} assigned to you successfully.')
    else:
        messages.warning(request, 'This report is already assigned to another technician.')
    
    return redirect('lab-report-queue')


@login_required(login_url='admin-login')
def update_report_status(request, report_id):
    """Update report status with notifications"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        technician_comments = request.POST.get('technician_comments', '')
        lab_notes = request.POST.get('lab_notes', '')
        
        if new_status in dict(Report.REPORT_STATUS_CHOICES):
            old_status = report.status
            report.status = new_status
            report.technician_comments = technician_comments
            report.lab_notes = lab_notes
            report.updated_at = timezone.now()
            
            # Set delivery date if completed
            if new_status == 'completed':
                report.delivery_date = timezone.now()
            
            report.save()
            
            # Send notifications
            send_report_status_notification(report, old_status, new_status)
            
            messages.success(request, f'Report status updated to {report.get_status_display()}')
            
            # Redirect based on status
            if new_status == 'completed':
                return redirect('upload-report-pdf', report_id=report.report_id)
            
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('lab-report-queue')


@login_required(login_url='admin-login')
def upload_report_pdf(request, report_id):
    """Upload PDF report with automatic notifications"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    if request.method == 'POST':
        pdf_file = request.FILES.get('report_pdf')
        result = request.POST.get('result', '')
        unit = request.POST.get('unit', '')
        referred_value = request.POST.get('referred_value', '')
        
        if pdf_file:
            # Validate file type
            if not pdf_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Please upload a PDF file only.')
                return redirect('upload-report-pdf', report_id=report_id)
            
            # Update report
            report.report_pdf = pdf_file
            report.result = result
            report.unit = unit
            report.referred_value = referred_value
            report.status = 'completed'
            report.delivery_date = timezone.now()
            report.save()
            
            # Send notifications
            send_report_completion_notification(report)
            
            messages.success(request, f'Report PDF uploaded successfully! Patient and doctor have been notified.')
            return redirect('lab-dashboard')
        else:
            messages.error(request, 'Please select a PDF file to upload.')
    
    context = {
        'lab_worker': lab_worker,
        'report': report,
    }
    
    return render(request, 'hospital_admin/upload-report-pdf.html', context)


@login_required(login_url='admin-login')
def my_assigned_reports(request):
    """View reports assigned to current technician"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'active')
    
    # Base queryset
    reports = Report.objects.filter(assigned_technician=lab_worker)
    
    if status_filter == 'active':
        reports = reports.filter(status__in=['collected', 'processing'])
    elif status_filter == 'completed':
        reports = reports.filter(status__in=['completed', 'delivered'])
    elif status_filter != 'all':
        reports = reports.filter(status=status_filter)
    
    reports = reports.order_by('-updated_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'lab_worker': lab_worker,
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'hospital_admin/my-assigned-reports.html', context)


@login_required(login_url='admin-login')
def report_detail_view(request, report_id):
    """Detailed view of a specific report"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    context = {
        'lab_worker': lab_worker,
        'report': report,
    }
    
    return render(request, 'hospital_admin/report-detail.html', context)


# ==================== NOTIFICATION FUNCTIONS ====================

def send_report_status_notification(report, old_status, new_status):
    """Send notifications when report status changes"""
    try:
        # Prepare notification message
        status_messages = {
            'collected': 'Sample has been collected and is being processed',
            'processing': 'Report is currently under processing',
            'completed': 'Report has been completed and is ready for delivery',
            'delivered': 'Report has been delivered successfully'
        }
        
        message = status_messages.get(new_status, f'Report status updated to {new_status}')
        
        # Send email to patient if email exists
        if report.patient and report.patient.email:
            subject = f'Lab Report Update - Report #{report.report_id}'
            html_message = render_to_string('hospital_admin/emails/report_status_update.html', {
                'report': report,
                'patient': report.patient,
                'message': message,
                'new_status': new_status
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [report.patient.email],
                html_message=html_message,
                fail_silently=True
            )
            
            # Update notification flag
            report.patient_notified = True
            report.save()
            
    except Exception as e:
        print(f"Error sending notification: {e}")


def send_report_completion_notification(report):
    """Send notification when report is completed"""
    try:
        # Send to patient
        if report.patient and report.patient.email:
            subject = f'Lab Report Ready - Report #{report.report_id}'
            html_message = render_to_string('hospital_admin/emails/report_completed.html', {
                'report': report,
                'patient': report.patient,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [report.patient.email],
                html_message=html_message,
                fail_silently=True
            )
        
        # Send to doctor if exists
        if report.doctor and report.doctor.email:
            subject = f'Patient Lab Report Ready - {report.patient.name}'
            html_message = render_to_string('hospital_admin/emails/doctor_report_notification.html', {
                'report': report,
                'doctor': report.doctor,
                'patient': report.patient,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [report.doctor.email],
                html_message=html_message,
                fail_silently=True
            )
        
        # Update notification flags
        report.patient_notified = True
        report.doctor_notified = True
        report.save()
        
    except Exception as e:
        print(f"Error sending completion notification: {e}")


@login_required(login_url='admin-login')
def bulk_report_actions(request):
    """Handle bulk actions on reports"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        report_ids = request.POST.getlist('selected_reports')
        
        if not report_ids:
            messages.warning(request, 'Please select at least one report.')
            return redirect('lab-report-queue')
        
        lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
        
        if action == 'assign_to_me':
            updated = Report.objects.filter(
                report_id__in=report_ids,
                assigned_technician__isnull=True
            ).update(
                assigned_technician=lab_worker,
                status='collected'
            )
            messages.success(request, f'{updated} reports assigned to you successfully.')
            
        elif action == 'mark_processing':
            updated = Report.objects.filter(
                report_id__in=report_ids,
                assigned_technician=lab_worker
            ).update(status='processing')
            messages.success(request, f'{updated} reports marked as processing.')
            
        elif action == 'mark_completed':
            updated = Report.objects.filter(
                report_id__in=report_ids,
                assigned_technician=lab_worker
            ).update(
                status='completed',
                delivery_date=timezone.now()
            )
            messages.success(request, f'{updated} reports marked as completed.')
    
    return redirect('lab-report-queue')

@csrf_exempt
@login_required(login_url='admin-login')
def lab_test_queue(request):
    """Lab worker view to see all prescribed tests and manage them"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get status filter
    status_filter = request.GET.get('status', 'all')
    
    # Get all prescribed tests with proper patient information (most recent first)
    all_tests = Prescription_test.objects.select_related(
        'prescription', 
        'prescription__patient',
        'prescription__patient__user', 
        'prescription__doctor'
    ).order_by('-test_id')  # Order by test_id descending to get newest first
    
    # Count statistics and filter
    test_queue = []
    stats = {
        'prescribed': 0, 
        'paid': 0,
        'collected': 0, 
        'processing': 0, 
        'completed': 0,
        'unpaid': 0
    }
    
    for test in all_tests:
        # Use the test_status from the model directly (with fallback)
        current_status = getattr(test, 'test_status', 'prescribed')
        
        # Count statistics
        if current_status in stats:
            stats[current_status] += 1
        
        # Count payment status
        if test.test_info_pay_status == 'unpaid':
            stats['unpaid'] += 1
        
        # Apply status filter
        if status_filter == 'all' or current_status == status_filter:
            # Add payment status info for display
            test.payment_status = test.test_info_pay_status
            # Allow collection for paid tests OR COD tests
            test.can_collect = (test.test_info_pay_status in ['paid', 'cod', 'cash_on_delivery', 'unpaid']) and current_status in ['prescribed', 'paid']
            test.can_process = current_status == 'collected'
            test.can_complete = current_status == 'processing'
            
            # Set the status for template display
            test.test_status = current_status
            
            # Add patient information for display
            if test.prescription and test.prescription.patient:
                patient = test.prescription.patient
                test.patient_name = f"{patient.user.first_name} {patient.user.last_name}".strip() or patient.user.username
                test.patient_age = getattr(patient, 'age', 'N/A')
                test.patient_phone = getattr(patient, 'phone', 'N/A')
                test.patient_id = patient.patient_id
            else:
                test.patient_name = 'Unknown Patient'
                test.patient_age = 'N/A'
                test.patient_phone = 'N/A'
                test.patient_id = 'N/A'
            
            test_queue.append(test)
    
    context = {
        'lab_worker': lab_worker,
        'test_queue': test_queue,
        'status_filter': status_filter,
        'stats': stats,
        'total_tests': len(all_tests)
    }
    return render(request, 'hospital_admin/lab-test-queue.html', context)

@csrf_exempt
@login_required(login_url='admin-login')
def lab_update_test_status(request):
    """AJAX endpoint to update test status"""
    if not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Not authorized'})
    
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        new_status = request.POST.get('status')
        
        try:
            lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
            test = Prescription_test.objects.get(test_id=test_id)
            
            # Check payment status before allowing collection (allow COD tests)
            if new_status == 'collected' and test.test_info_pay_status not in ['paid', 'cod_pending', 'cod']:
                return JsonResponse({
                    'success': False, 
                    'message': 'Payment must be completed or COD arranged before sample collection'
                })
            
            # Update the test status directly in Prescription_test
            old_status = getattr(test, 'test_status', 'prescribed')
            
            # Only update if the field exists
            if hasattr(test, 'test_status'):
                test.test_status = new_status
            if hasattr(test, 'assigned_technician'):
                test.assigned_technician = lab_worker
            if hasattr(test, 'updated_at'):
                test.updated_at = timezone.now()
            
            test.save()
            
            # Also create/update Report for tracking (only if patient exists)
            report = None
            if test.prescription and test.prescription.patient:
                report, created = Report.objects.get_or_create(
                    patient=test.prescription.patient,
                    test_name=test.test_name,
                    defaults={
                        'doctor': test.prescription.doctor if test.prescription.doctor else None,
                        'assigned_technician': lab_worker,
                        'status': new_status,
                        'uploaded_at': timezone.now()
                    }
                )
                
                if not created and report:
                    # Update existing report
                    report.status = new_status
                    report.assigned_technician = lab_worker
                    
                    # Set timestamps based on status
                    if new_status == 'collected':
                        report.collection_date = timezone.now()
                    elif new_status == 'processing':
                        report.receiving_date = timezone.now()
                    
                    report.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Test status updated from {old_status} to {new_status}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
@login_required(login_url='admin-login')
def lab_complete_test(request):
    """AJAX endpoint to complete test with results"""
    if not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Not authorized'})
    
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        result = request.POST.get('result')
        unit = request.POST.get('unit', '')
        normal_range = request.POST.get('normal_range', '')
        comments = request.POST.get('comments', '')
        
        try:
            lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
            test = Prescription_test.objects.get(test_id=test_id)
            
            # Update the test status to completed
            if hasattr(test, 'test_status'):
                test.test_status = 'completed'
            if hasattr(test, 'assigned_technician'):
                test.assigned_technician = lab_worker
            if hasattr(test, 'updated_at'):
                test.updated_at = timezone.now()
            test.save()
            
            # Get or create report with results
            report, created = Report.objects.get_or_create(
                patient=test.prescription.patient,
                test_name=test.test_name,
                defaults={
                    'doctor': test.prescription.doctor,
                    'assigned_technician': lab_worker,
                    'status': 'completed',
                    'result': result,
                    'unit': unit,
                    'normal_range': normal_range,
                    'comments': comments,
                    'uploaded_at': timezone.now()
                }
            )
            
            if not created:
                # Update existing report
                report.status = 'completed'
                report.result = result
                report.unit = unit
                report.normal_range = normal_range
                report.comments = comments
                report.assigned_technician = lab_worker
                report.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Test completed successfully! Report generated for {test.test_name}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
@login_required(login_url='admin-login')
def update_test_payment_status(request):
    """AJAX endpoint to update test payment status"""
    if not request.user.is_hospital_admin and not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Not authorized'})
    
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        payment_status = request.POST.get('payment_status')
        
        try:
            test = Prescription_test.objects.get(test_id=test_id)
            
            # Update payment status
            old_status = test.test_info_pay_status
            test.test_info_pay_status = payment_status
            
            if payment_status == 'paid':
                test.payment_date = timezone.now()
                # If test was prescribed and now paid, it's ready for collection
                if test.test_status == 'prescribed':
                    test.test_status = 'paid'
            
            test.updated_at = timezone.now()
            test.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Payment status updated from {old_status} to {payment_status}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
@login_required(login_url='admin-login')
def upload_test_result(request, test_id):
    """View for uploading test result PDF"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    try:
        test = Prescription_test.objects.get(test_id=test_id)
        patient = test.prescription.patient
    except Prescription_test.DoesNotExist:
        messages.error(request, 'Test not found.')
        return redirect('mypatient-list')
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('result_pdf')
        
        if not uploaded_file:
            messages.error(request, 'Please select a PDF file to upload.')
            return render(request, 'hospital_admin/upload-test-result.html', {
                'test': test,
                'lab_worker': lab_worker
            })
        
        # Create or update report
        report, created = Report.objects.get_or_create(
            patient=patient,
            test_name=test.test_name,
            defaults={
                'doctor': test.prescription.doctor,
                'assigned_technician': lab_worker,
                'status': 'completed',
                'delivery_date': timezone.now(),
                'report_pdf': uploaded_file
            }
        )
        
        if not created:
            report.report_pdf = uploaded_file
            report.status = 'completed'
            report.delivery_date = timezone.now()
            report.assigned_technician = lab_worker
            report.save()
        
        # Update test status to completed
        test.test_status = 'completed'
        test.updated_at = timezone.now()
        test.save()
        
        messages.success(request, f'Test result uploaded successfully for {test.test_name}')
        return redirect('mypatient-list')
    
    context = {
        'test': test,
        'lab_worker': lab_worker
    }
    return render(request, 'hospital_admin/upload-test-result.html', context)

@csrf_exempt
@login_required(login_url='admin-login')
def test_details(request, test_id):
    """View test details"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    try:
        test = Prescription_test.objects.select_related(
            'prescription',
            'prescription__patient',
            'prescription__patient__user',
            'prescription__doctor'
        ).get(test_id=test_id)
        
        # Get related report if exists
        try:
            report = Report.objects.get(
                patient=test.prescription.patient,
                test_name=test.test_name
            )
        except Report.DoesNotExist:
            report = None
        
    except Prescription_test.DoesNotExist:
        messages.error(request, 'Test not found.')
        return redirect('mypatient-list')
    
    context = {
        'test': test,
        'report': report,
        'lab_worker': lab_worker
    }
    return render(request, 'hospital_admin/test-details.html', context)


# ==================== ENHANCED LAB REPORT MANAGEMENT ====================

@login_required(login_url='admin-login')
def lab_report_details(request, report_id):
    """Comprehensive lab report details with history tracking"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    report = get_object_or_404(Report, report_id=report_id)
    
    # Get related test information
    prescription_test = None
    try:
        prescription_test = Prescription_test.objects.select_related(
            'prescription__doctor', 'prescription__patient__user'
        ).get(
            prescription__patient=report.patient,
            test_name=report.test_name
        )
    except Prescription_test.DoesNotExist:
        pass
    
    # Report history tracking
    report_history = []
    
    # Add creation entry
    report_history.append({
        'action': 'Report Created',
        'timestamp': report.uploaded_at,
        'user': 'System',
        'details': f'Report #{report.report_id} created for {report.patient.user.get_full_name() if report.patient else "Unknown Patient"}',
        'status': 'pending',
        'icon': 'fa-plus-circle',
        'color': 'info'
    })
    
    # Add assignment entry if assigned
    if report.assigned_technician:
        report_history.append({
            'action': 'Assigned to Technician',
            'timestamp': report.updated_at,
            'user': report.assigned_technician.name,
            'details': f'Assigned to {report.assigned_technician.name}',
            'status': 'assigned',
            'icon': 'fa-user-check',
            'color': 'primary'
        })
    
    # Add collection entry
    if hasattr(report, 'collection_date') and report.collection_date:
        report_history.append({
            'action': 'Sample Collected',
            'timestamp': report.collection_date,
            'user': report.assigned_technician.name if report.assigned_technician else 'Unknown',
            'details': 'Sample collected and ready for processing',
            'status': 'collected',
            'icon': 'fa-vial',
            'color': 'warning'
        })
    
    # Add processing entry
    if report.status == 'processing':
        report_history.append({
            'action': 'Processing Started',
            'timestamp': report.updated_at,
            'user': report.assigned_technician.name if report.assigned_technician else 'Unknown',
            'details': 'Test processing initiated',
            'status': 'processing',
            'icon': 'fa-cogs',
            'color': 'info'
        })
    
    # Add completion entry
    if report.status == 'completed':
        report_history.append({
            'action': 'Report Completed',
            'timestamp': report.delivery_date or report.updated_at,
            'user': report.assigned_technician.name if report.assigned_technician else 'Unknown',
            'details': 'Report completed and ready for delivery',
            'status': 'completed',
            'icon': 'fa-check-circle',
            'color': 'success'
        })
    
    # Sort history by timestamp
    report_history.sort(key=lambda x: x['timestamp'])
    
    # Quality control information
    qc_info = {
        'calibration_status': 'Valid',
        'control_results': 'Within Range',
        'equipment_status': 'Functional',
        'last_calibration': timezone.now() - timedelta(days=2),
        'next_calibration': timezone.now() + timedelta(days=5),
        'qc_level': 'Level 2',
        'batch_number': f'B{timezone.now().strftime("%Y%m%d")}001',
    }
    
    # Related reports for same patient
    related_reports = Report.objects.filter(
        patient=report.patient
    ).exclude(report_id=report.report_id).order_by('-uploaded_at')[:5]
    
    # Technical details
    technical_info = {
        'method': 'Automated Analysis',
        'instrument': 'Bio-Analyzer 3000',
        'reagent_lot': 'RL-2024-089',
        'temperature': '25°C',
        'humidity': '45%',
        'operator': report.assigned_technician.name if report.assigned_technician else 'Unknown',
    }
    
    context = {
        'lab_worker': lab_worker,
        'report': report,
        'prescription_test': prescription_test,
        'report_history': report_history,
        'qc_info': qc_info,
        'related_reports': related_reports,
        'technical_info': technical_info,
    }
    
    return render(request, 'hospital_admin/lab-report-details.html', context)


# ==================== LAB ANALYTICS AND REPORTING ====================

@login_required(login_url='admin-login')
def lab_analytics_dashboard(request):
    """Comprehensive lab analytics and reporting dashboard"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Date ranges for analysis
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    quarter_ago = today - timedelta(days=90)
    year_ago = today - timedelta(days=365)
    
    # === COMPREHENSIVE STATISTICS ===
    
    # Test volume analytics
    test_analytics = {
        'daily_tests': Prescription_test.objects.filter(
            updated_at__date=today
        ).count(),
        'weekly_tests': Prescription_test.objects.filter(
            updated_at__date__gte=week_ago
        ).count(),
        'monthly_tests': Prescription_test.objects.filter(
            updated_at__date__gte=month_ago
        ).count(),
        'quarterly_tests': Prescription_test.objects.filter(
            updated_at__date__gte=quarter_ago
        ).count(),
        'yearly_tests': Prescription_test.objects.filter(
            updated_at__date__gte=year_ago
        ).count(),
    }
    
    # Test type analysis (top 10 most requested tests)
    test_type_stats = Prescription_test.objects.values(
        'test_name'
    ).annotate(
        count=Count('test_id'),
        completed_count=Count('test_id', filter=Q(test_status='completed')),
        pending_count=Count('test_id', filter=Q(test_status__in=['paid', 'collected', 'processing']))
    ).order_by('-count')[:10]
    
    # Department analysis
    department_stats = Prescription.objects.filter(
        create_date__gte=(today - timedelta(days=30)).strftime('%Y-%m-%d')
    ).values(
        'doctor__department'
    ).annotate(
        total_tests=Count('prescription_test'),
        total_patients=Count('patient', distinct=True),
        avg_tests_per_patient=Count('prescription_test') / Count('patient', distinct=True)
    ).order_by('-total_tests')[:10]
    
    # Technician performance comparison
    technician_performance = Clinical_Laboratory_Technician.objects.annotate(
        weekly_assigned_tests=Count(
            'assigned_tests',
            filter=Q(assigned_tests__updated_at__date__gte=week_ago)
        ),
        weekly_completed_tests=Count(
            'assigned_tests',
            filter=Q(
                assigned_tests__test_status='completed',
                assigned_tests__updated_at__date__gte=week_ago
            )
        ),
        weekly_pending_tests=Count(
            'assigned_tests',
            filter=Q(
                assigned_tests__test_status__in=['collected', 'processing'],
                assigned_tests__updated_at__date__gte=week_ago
            )
        )
    ).order_by('-weekly_completed_tests')[:8]
    
    # Add completion rate for each technician
    for tech in technician_performance:
        if tech.weekly_assigned_tests > 0:
            tech.completion_rate = round((tech.weekly_completed_tests / tech.weekly_assigned_tests) * 100, 1)
        else:
            tech.completion_rate = 0
    
    # Turnaround time analysis
    turnaround_stats = {
        'avg_completion_time': '2.3 hours',
        'fastest_completion': '45 minutes',
        'slowest_completion': '6.2 hours',
        'target_time': '2 hours',
        'on_time_percentage': 87.5,
        'same_day_percentage': 94.2,
        'next_day_percentage': 5.8,
    }
    
    # Revenue analytics
    try:
        revenue_analytics = {
            'daily_revenue': Prescription_test.objects.filter(
                test_info_pay_status='paid',
                updated_at__date=today
            ).aggregate(
                total=Sum('test_cost')
            )['total'] or 0,
            'weekly_revenue': Prescription_test.objects.filter(
                test_info_pay_status='paid',
                updated_at__date__gte=week_ago
            ).aggregate(
                total=Sum('test_cost')
            )['total'] or 0,
            'monthly_revenue': Prescription_test.objects.filter(
                test_info_pay_status='paid',
                updated_at__date__gte=month_ago
            ).aggregate(
                total=Sum('test_cost')
            )['total'] or 0,
        }
    except:
        # Fallback if test_cost field doesn't exist
        revenue_analytics = {
            'daily_revenue': 0,
            'weekly_revenue': 0,
            'monthly_revenue': 0,
        }
    
    # Quality metrics
    quality_metrics = {
        'accuracy_rate': 98.7,
        'repeat_rate': 1.3,
        'calibration_compliance': 99.2,
        'equipment_uptime': 97.8,
        'patient_satisfaction': 4.6,
        'error_rate': 0.8,
        'contamination_rate': 0.2,
    }
    
    # Trend data for charts (last 7 days)
    daily_trends = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_count = Prescription_test.objects.filter(
            updated_at__date=date,
            test_status='completed'
        ).count()
        daily_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'date_display': date.strftime('%b %d'),
            'completed_tests': daily_count,
        })
    daily_trends.reverse()
    
    # Monthly trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)  # Ensure we get end of month
        month_end = month_end - timedelta(days=month_end.day)
        
        monthly_count = Prescription_test.objects.filter(
            updated_at__date__gte=month_start,
            updated_at__date__lte=month_end,
            test_status='completed'
        ).count()
        
        monthly_trends.append({
            'month': month_start.strftime('%Y-%m'),
            'month_display': month_start.strftime('%B %Y'),
            'completed_tests': monthly_count,
        })
    monthly_trends.reverse()
    
    # Equipment utilization (mock data)
    equipment_stats = [
        {'name': 'Bio-Analyzer 3000', 'utilization': 89.5, 'uptime': 98.2, 'tests_today': 45},
        {'name': 'Hematology Analyzer', 'utilization': 76.8, 'uptime': 99.1, 'tests_today': 32},
        {'name': 'Chemistry Analyzer', 'utilization': 82.3, 'uptime': 97.8, 'tests_today': 38},
        {'name': 'Immunology System', 'utilization': 65.2, 'uptime': 99.5, 'tests_today': 28},
    ]
    
    context = {
        'lab_worker': lab_worker,
        'test_analytics': test_analytics,
        'test_type_stats': test_type_stats,
        'department_stats': department_stats,
        'technician_performance': technician_performance,
        'turnaround_stats': turnaround_stats,
        'revenue_analytics': revenue_analytics,
        'quality_metrics': quality_metrics,
        'daily_trends': daily_trends,
        'monthly_trends': monthly_trends,
        'equipment_stats': equipment_stats,
        'today': today,
    }
    
    return render(request, 'hospital_admin/lab-analytics.html', context)


# ==================== LAB TECHNICIAN MANAGEMENT ====================

@login_required(login_url='admin-login')
def lab_technician_management(request):
    """Lab technician profile and workload management system"""
    if not request.user.is_labworker and not request.user.is_hospital_admin:
        return redirect('admin-logout')
    
    # Get all lab technicians
    technicians = Clinical_Laboratory_Technician.objects.all()
    
    # Add workload information to each technician
    for tech in technicians:
        # Current workload
        tech.current_assigned = Prescription_test.objects.filter(
            assigned_technician=tech,
            test_status__in=['paid', 'collected', 'processing']
        ).count()
        
        # Completed this week
        week_ago = timezone.now().date() - timedelta(days=7)
        tech.completed_week = Prescription_test.objects.filter(
            assigned_technician=tech,
            test_status='completed',
            updated_at__date__gte=week_ago
        ).count()
        
        # Performance metrics
        total_assigned = Prescription_test.objects.filter(assigned_technician=tech).count()
        completed_total = Prescription_test.objects.filter(
            assigned_technician=tech,
            test_status='completed'
        ).count()
        
        tech.completion_rate = round((completed_total / total_assigned * 100), 1) if total_assigned > 0 else 0
        tech.workload_level = 'High' if tech.current_assigned > 15 else 'Medium' if tech.current_assigned > 5 else 'Low'
    
    # Workload distribution
    workload_distribution = {
        'balanced': sum(1 for t in technicians if 5 <= t.current_assigned <= 15),
        'overloaded': sum(1 for t in technicians if t.current_assigned > 15),
        'underutilized': sum(1 for t in technicians if t.current_assigned < 5),
    }
    
    context = {
        'technicians': technicians,
        'workload_distribution': workload_distribution,
        'total_technicians': technicians.count(),
    }
    
    return render(request, 'hospital_admin/lab-technician-management.html', context)


# ==================== LAB OPERATIONS MANAGEMENT ====================

@login_required(login_url='admin-login')
def lab_operations_management(request):
    """Lab equipment and operations management"""
    if not request.user.is_labworker and not request.user.is_hospital_admin:
        return redirect('admin-logout')
    
    # Test catalog management
    available_tests = Test_Information.objects.all().order_by('test_name')
    
    # Equipment information (mock data - in real system would come from equipment management module)
    equipment_list = [
        {
            'name': 'Bio-Analyzer 3000',
            'type': 'Biochemistry',
            'status': 'Operational',
            'last_calibration': timezone.now() - timedelta(days=3),
            'next_calibration': timezone.now() + timedelta(days=4),
            'maintenance_due': timezone.now() + timedelta(days=15),
            'tests_capacity': 100,
            'tests_completed_today': 45,
        },
        {
            'name': 'Hematology Analyzer HA-500',
            'type': 'Hematology',
            'status': 'Operational',
            'last_calibration': timezone.now() - timedelta(days=1),
            'next_calibration': timezone.now() + timedelta(days=6),
            'maintenance_due': timezone.now() + timedelta(days=8),
            'tests_capacity': 80,
            'tests_completed_today': 32,
        },
        {
            'name': 'Chemistry Analyzer CA-200',
            'type': 'Clinical Chemistry',
            'status': 'Maintenance Required',
            'last_calibration': timezone.now() - timedelta(days=5),
            'next_calibration': timezone.now() + timedelta(days=2),
            'maintenance_due': timezone.now() - timedelta(days=2),  # Overdue
            'tests_capacity': 120,
            'tests_completed_today': 0,  # Not operational
        },
        {
            'name': 'Immunology System IS-150',
            'type': 'Immunology',
            'status': 'Operational',
            'last_calibration': timezone.now() - timedelta(days=2),
            'next_calibration': timezone.now() + timedelta(days=5),
            'maintenance_due': timezone.now() + timedelta(days=20),
            'tests_capacity': 60,
            'tests_completed_today': 28,
        },
    ]
    
    # Calculate equipment utilization
    for equipment in equipment_list:
        if equipment['tests_capacity'] > 0:
            equipment['utilization_percent'] = round(
                (equipment['tests_completed_today'] / equipment['tests_capacity']) * 100, 1
            )
        else:
            equipment['utilization_percent'] = 0
    
    # Workflow optimization data
    workflow_stats = {
        'avg_sample_processing_time': '1.8 hours',
        'bottleneck_stage': 'Sample Preparation',
        'efficiency_score': 85.7,
        'automation_level': 73.2,
        'peak_hours': '10:00 AM - 2:00 PM',
        'recommended_capacity': 150,
        'current_capacity': 120,
    }
    
    # Supply inventory (mock data)
    supply_inventory = [
        {'item': 'Reagent Kit A', 'current_stock': 45, 'min_threshold': 20, 'status': 'Good'},
        {'item': 'Control Serum Level 1', 'current_stock': 12, 'min_threshold': 15, 'status': 'Low'},
        {'item': 'Sample Tubes (100ml)', 'current_stock': 250, 'min_threshold': 100, 'status': 'Good'},
        {'item': 'Calibration Standards', 'current_stock': 8, 'min_threshold': 10, 'status': 'Critical'},
        {'item': 'Quality Control Kit', 'current_stock': 25, 'min_threshold': 12, 'status': 'Good'},
    ]
    
    context = {
        'available_tests': available_tests,
        'equipment_list': equipment_list,
        'workflow_stats': workflow_stats,
        'supply_inventory': supply_inventory,
    }
    
    return render(request, 'hospital_admin/lab-operations.html', context)


# ==================== LAB COMMUNICATION SYSTEM ====================

@login_required(login_url='admin-login')
def lab_notifications_center(request):
    """Lab notification system and communication center"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Critical alerts
    critical_alerts = []
    
    # Equipment alerts
    critical_alerts.append({
        'type': 'equipment',
        'level': 'critical',
        'title': 'Equipment Maintenance Overdue',
        'message': 'Chemistry Analyzer CA-200 requires immediate maintenance',
        'timestamp': timezone.now() - timedelta(hours=2),
        'action_required': True,
        'icon': 'fa-exclamation-triangle',
        'color': 'danger'
    })
    
    # Quality control alerts
    critical_alerts.append({
        'type': 'quality',
        'level': 'warning',
        'title': 'QC Results Outside Range',
        'message': 'Control Level 2 results for Glucose test outside acceptable range',
        'timestamp': timezone.now() - timedelta(minutes=30),
        'action_required': True,
        'icon': 'fa-chart-line',
        'color': 'warning'
    })
    
    # Supply alerts
    critical_alerts.append({
        'type': 'supply',
        'level': 'warning',
        'title': 'Low Inventory Alert',
        'message': 'Calibration Standards inventory below minimum threshold',
        'timestamp': timezone.now() - timedelta(hours=1),
        'action_required': False,
        'icon': 'fa-boxes',
        'color': 'warning'
    })
    
    # Urgent test alerts
    urgent_tests = Prescription_test.objects.filter(
        test_info_pay_status='paid',
        test_status__in=['paid', 'collected'],
        updated_at__date__lt=timezone.now().date() - timedelta(days=1)
    ).select_related('prescription__patient__user', 'prescription__doctor')[:5]
    
    for test in urgent_tests:
        days_pending = (timezone.now().date() - test.updated_at.date()).days
        critical_alerts.append({
            'type': 'urgent_test',
            'level': 'high' if days_pending > 2 else 'medium',
            'title': f'Urgent Test Pending - {test.test_name}',
            'message': f'Patient: {test.prescription.patient.user.get_full_name()} - {days_pending} days pending',
            'timestamp': test.updated_at,
            'action_required': True,
            'icon': 'fa-clock',
            'color': 'danger' if days_pending > 2 else 'warning'
        })
    
    # Sort alerts by timestamp (newest first)
    critical_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # System notifications
    system_notifications = [
        {
            'title': 'System Maintenance Scheduled',
            'message': 'Lab management system will undergo maintenance on Sunday 2:00 AM - 4:00 AM',
            'timestamp': timezone.now() - timedelta(hours=6),
            'type': 'info',
            'icon': 'fa-info-circle'
        },
        {
            'title': 'New Test Added to Catalog',
            'message': 'HbA1c test has been added to the available test catalog',
            'timestamp': timezone.now() - timedelta(days=1),
            'type': 'success',
            'icon': 'fa-plus-circle'
        },
        {
            'title': 'Training Session Reminder',
            'message': 'Monthly safety training session scheduled for Friday 3:00 PM',
            'timestamp': timezone.now() - timedelta(days=2),
            'type': 'info',
            'icon': 'fa-graduation-cap'
        },
    ]
    
    # Communication channels
    communication_channels = {
        'internal_messages': 12,
        'doctor_queries': 3,
        'patient_inquiries': 7,
        'system_alerts': len(critical_alerts),
        'equipment_notifications': 2,
    }
    
    context = {
        'lab_worker': lab_worker,
        'critical_alerts': critical_alerts[:10],  # Show top 10
        'system_notifications': system_notifications,
        'communication_channels': communication_channels,
        'total_alerts': len(critical_alerts),
    }
    
    return render(request, 'hospital_admin/lab-notifications.html', context)


# ==================== ENHANCED LAB TECHNICIAN ORDER MANAGEMENT ====================

@login_required(login_url='admin-login')
def lab_technician_order_management(request):
    """Comprehensive lab technician order management with complete patient-lab workflow"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # === IMPORT REQUIRED MODELS ===
    from doctor.models import testOrder, testCart, Prescription_test, Prescription
    from django.db.models import Q, Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # === GET ALL ORDERS WITH COMPREHENSIVE DATA ===
    # Test orders from testOrder model (online/COD orders)
    all_test_orders = testOrder.objects.select_related(
        'user', 'user__patient'
    ).prefetch_related(
        'orderitems', 'orderitems__item'
    ).order_by('-created')
    
    # Prescription tests (doctor prescribed tests)
    all_prescription_tests = Prescription_test.objects.select_related(
        'prescription', 'prescription__patient', 'prescription__patient__user',
        'prescription__doctor', 'assigned_technician'
    ).order_by('-created_at')
    
    # === ORDER CATEGORIZATION ===
    # Online paid orders (ready for collection)
    paid_orders = all_test_orders.filter(
        payment_status='paid',
        ordered=True
    ).exclude(
        payment_status__in=['collected', 'processing', 'completed']
    )
    
    # COD orders (need payment collection + sample collection)
    cod_orders = all_test_orders.filter(
        Q(payment_status='cod_pending') | Q(payment_status='cash_on_delivery'),
        ordered=True
    ).exclude(
        payment_status__in=['collected', 'processing', 'completed']
    )
    
    # Processing orders (samples collected, tests in progress)
    processing_orders = []
    
    # Add testOrders in processing
    processing_test_orders = all_test_orders.filter(
        payment_status__in=['collected', 'processing'],
        ordered=True
    )
    processing_orders.extend(processing_test_orders)
    
    # Add prescription tests in processing
    processing_prescription_tests = all_prescription_tests.filter(
        test_status__in=['collected', 'processing'],
        test_info_pay_status='paid'
    )
    processing_orders.extend(processing_prescription_tests)
    
    # Completed orders
    completed_orders = []
    
    # Add completed testOrders
    completed_test_orders = all_test_orders.filter(
        payment_status='completed',
        ordered=True
    )
    completed_orders.extend(completed_test_orders)
    
    # Add completed prescription tests
    completed_prescription_tests = all_prescription_tests.filter(
        test_status='completed',
        test_info_pay_status='paid'
    )
    completed_orders.extend(completed_prescription_tests)
    
    # Failed payment orders
    failed_orders = all_test_orders.filter(
        payment_status='failed',
        ordered=True
    )
    
    # === ORDER STATISTICS ===
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    order_stats = {
        'prescribed': all_prescription_tests.filter(test_info_pay_status='unpaid').count(),
        'paid': paid_orders.count(),
        'cod': cod_orders.count(),
        'collected': all_test_orders.filter(payment_status='collected').count() + 
                    all_prescription_tests.filter(test_status='collected').count(),
        'processing': len(processing_orders),
        'completed': len(completed_orders),
        'failed': failed_orders.count(),
    }
    
    # Performance metrics
    completed_today = len([o for o in completed_orders if hasattr(o, 'updated_at') and 
                          o.updated_at.date() == today]) + \
                     len([o for o in completed_orders if hasattr(o, 'created') and 
                          o.created.date() == today])
    
    completed_week = len([o for o in completed_orders if hasattr(o, 'updated_at') and 
                         o.updated_at.date() >= week_ago]) + \
                    len([o for o in completed_orders if hasattr(o, 'created') and 
                         o.created.date() >= week_ago])
    
    # Average wait time calculation (simplified)
    avg_wait_time = "2-3 hours"
    priority_count = all_prescription_tests.filter(
        test_status__in=['collected', 'processing'],
        created_at__date__lte=today - timedelta(days=1)
    ).count()
    
    context = {
        'lab_worker': lab_worker,
        'order_stats': order_stats,
        'paid_orders': paid_orders,
        'cod_orders': cod_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'failed_orders': failed_orders,
        'completed_today': completed_today,
        'completed_week': completed_week,
        'avg_wait_time': avg_wait_time,
        'priority_count': priority_count,
    }
    
    return render(request, 'hospital_admin/lab-technician-order-management.html', context)


@login_required(login_url='admin-login')
def lab_update_order_status(request):
    """Update lab order status - comprehensive status management"""
    if request.method != 'POST' or not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    try:
        from doctor.models import testOrder, Prescription_test
        
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order_type = request.POST.get('order_type', 'lab')
        
        if not order_id or not status:
            return JsonResponse({'success': False, 'message': 'Missing required parameters'})
        
        # Handle different order types
        if order_type == 'lab' or order_type == 'test':
            # Handle testOrder model
            try:
                order = testOrder.objects.get(id=order_id)
                
                # Update status based on current status and requested status
                if status == 'collected' and order.payment_status in ['paid', 'cod_pending', 'cash_on_delivery']:
                    order.payment_status = 'collected'
                    message = 'Sample collected successfully!'
                    
                elif status == 'processing' and order.payment_status == 'collected':
                    order.payment_status = 'processing'
                    message = 'Test processing started!'
                    
                elif status == 'completed' and order.payment_status == 'processing':
                    order.payment_status = 'completed'
                    message = 'Test completed successfully!'
                    
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid status transition'})
                
                order.save()
                
            except testOrder.DoesNotExist:
                # Try prescription test model
                try:
                    order = Prescription_test.objects.get(test_id=order_id)
                    
                    if status == 'collected' and order.test_status in ['prescribed', 'paid']:
                        order.test_status = 'collected'
                        message = 'Sample collected successfully!'
                        
                    elif status == 'processing' and order.test_status == 'collected':
                        order.test_status = 'processing'
                        message = 'Test processing started!'
                        
                    elif status == 'completed' and order.test_status == 'processing':
                        order.test_status = 'completed'
                        message = 'Test completed successfully!'
                        
                    else:
                        return JsonResponse({'success': False, 'message': 'Invalid status transition'})
                    
                    order.save()
                    
                except Prescription_test.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Order not found'})
        
        # Send notification email to patient
        try:
            if hasattr(order, 'user') and order.user:
                patient_email = order.user.email
                patient_name = f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username
            elif hasattr(order, 'prescription') and order.prescription:
                patient_email = order.prescription.patient.user.email
                patient_name = f"{order.prescription.patient.user.first_name} {order.prescription.patient.user.last_name}".strip()
            else:
                patient_email = None
                patient_name = "Patient"
            
            if patient_email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                status_messages = {
                    'collected': 'Your lab sample has been collected and will be processed shortly.',
                    'processing': 'Your lab test is currently being processed in our laboratory.',
                    'completed': 'Your lab test results are ready. Please check your patient dashboard.'
                }
                
                send_mail(
                    subject=f'Lab Test Update - {status.title()}',
                    message=f'''
Dear {patient_name},

Your lab test status has been updated.

Status: {status.title()}
Order ID: #{order_id}
Update: {status_messages.get(status, 'Status updated')}

You can check your complete test results and reports in your patient dashboard.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[patient_email],
                    fail_silently=True,
                )
        except Exception as e:
            # Email sending failed, but order update was successful
            print(f"Email sending failed: {e}")
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating order: {str(e)}'})


@login_required(login_url='admin-login')
def lab_process_cod_payment(request):
    """Process COD payment collection for lab tests"""
    if request.method != 'POST' or not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    try:
        from doctor.models import testOrder
        
        order_id = request.POST.get('order_id')
        payment_method = request.POST.get('payment_method')
        amount_received = request.POST.get('amount_received')
        notes = request.POST.get('notes', '')
        
        if not all([order_id, payment_method, amount_received]):
            return JsonResponse({'success': False, 'message': 'Missing required payment information'})
        
        try:
            amount_received = float(amount_received)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid amount format'})
        
        # Get the order
        try:
            order = testOrder.objects.get(id=order_id)
        except testOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        
        # Validate payment amount
        expected_amount = float(order.final_bill if hasattr(order, 'final_bill') and order.final_bill else order.total_amount)
        
        if amount_received < expected_amount:
            return JsonResponse({
                'success': False, 
                'message': f'Insufficient payment. Expected: ₹{expected_amount}, Received: ₹{amount_received}'
            })
        
        # Process payment
        order.payment_status = 'collected'  # Payment collected, sample collected
        order.trans_ID = f"COD_{order_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        order.save()
        
        # Create payment record (if you have a payment model)
        try:
            from razorpay_payment.models import RazorpayPayment
            
            RazorpayPayment.objects.create(
                razorpay_order_id=f"LAB_{order_id}",
                razorpay_payment_id=order.trans_ID,
                razorpay_signature="COD_PAYMENT",
                amount=amount_received,
                status="captured",
                payment_type="test",
                test_order=order,
                patient=order.user.patient if hasattr(order.user, 'patient') else None,
                name=f"{order.user.first_name} {order.user.last_name}".strip(),
                email=order.user.email
            )
        except Exception as e:
            print(f"Payment record creation failed: {e}")
        
        # Send confirmation email
        try:
            if order.user and order.user.email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject='Payment Confirmed - Lab Test Order',
                    message=f'''
Dear {order.user.first_name} {order.user.last_name},

Your cash payment has been successfully collected for your lab test order.

Order ID: #{order_id}
Amount Paid: ₹{amount_received}
Payment Method: {payment_method.title()}
Transaction ID: {order.trans_ID}

Your sample has been collected and will be processed shortly. You will receive another notification once your test results are ready.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                    fail_silently=True,
                )
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return JsonResponse({
            'success': True, 
            'message': f'COD payment of ₹{amount_received} collected successfully! Sample collection recorded.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error processing payment: {str(e)}'})


@login_required(login_url='admin-login')
def lab_complete_test_with_results(request):
    """Complete lab test with detailed results"""
    if request.method != 'POST' or not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    try:
        from doctor.models import testOrder, Prescription_test
        
        order_id = request.POST.get('order_id')
        test_results = request.POST.get('test_results')
        unit = request.POST.get('unit', '')
        normal_range = request.POST.get('normal_range', '')
        technician_comments = request.POST.get('technician_comments', '')
        report_status = request.POST.get('report_status', 'normal')
        
        if not order_id or not test_results:
            return JsonResponse({'success': False, 'message': 'Missing required test results'})
        
        lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
        
        # Try to find the order in testOrder first
        order = None
        order_type = None
        
        try:
            order = testOrder.objects.get(id=order_id)
            order_type = 'test_order'
        except testOrder.DoesNotExist:
            # Try prescription test
            try:
                order = Prescription_test.objects.get(test_id=order_id)
                order_type = 'prescription_test'
            except Prescription_test.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Order not found'})
        
        # Update order status
        if order_type == 'test_order':
            order.payment_status = 'completed'
        else:
            order.test_status = 'completed'
            order.assigned_technician = lab_worker
        
        order.save()
        
        # Create/Update test report
        try:
            # Try to import your report model
            from doctor.models import Test_report  # Adjust import as needed
            
            # Create comprehensive test report
            report_data = {
                'test_results': test_results,
                'unit': unit,
                'normal_range': normal_range,
                'technician_comments': technician_comments,
                'report_status': report_status,
                'technician_name': lab_worker.name or lab_worker.user.username,
                'completed_at': timezone.now(),
            }
            
            if order_type == 'test_order':
                # For testOrder, create report for each test
                for item in order.orderitems.all():
                    Test_report.objects.update_or_create(
                        test_name=item.test.test_name,
                        patient=order.user.patient if hasattr(order.user, 'patient') else None,
                        defaults=report_data
                    )
            else:
                # For prescription test
                Test_report.objects.update_or_create(
                    test_name=order.test_name,
                    patient=order.prescription.patient,
                    prescription=order.prescription,
                    defaults=report_data
                )
        
        except Exception as e:
            print(f"Report creation failed: {e}")
            # Continue even if report creation fails
        
        # Send completion notification
        try:
            patient_email = None
            patient_name = "Patient"
            
            if order_type == 'test_order' and order.user:
                patient_email = order.user.email
                patient_name = f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username
            elif order_type == 'prescription_test' and order.prescription:
                patient_email = order.prescription.patient.user.email
                patient_name = f"{order.prescription.patient.user.first_name} {order.prescription.patient.user.last_name}".strip()
            
            if patient_email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject='Lab Test Results Ready - Mahima Medicare',
                    message=f'''
Dear {patient_name},

Your lab test results are now ready for review.

Order ID: #{order_id}
Test Status: Completed
Completed By: {lab_worker.name or lab_worker.user.username}
Completion Date: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

Result Summary: {report_status.title()}

Please log into your patient dashboard to view your complete test results and download your report.

If you have any questions about your results, please consult with your doctor or contact our laboratory team.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[patient_email],
                    fail_silently=True,
                )
        except Exception as e:
            print(f"Email notification failed: {e}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Test completed successfully! Results saved and patient notified.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error completing test: {str(e)}'})


@login_required(login_url='admin-login')
def lab_handle_payment_failure(request):
    """Handle failed payment recovery for lab tests"""
    if request.method != 'POST' or not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    try:
        from doctor.models import testOrder
        
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')  # 'retry', 'convert_to_cod', 'cancel'
        
        if not order_id or not action:
            return JsonResponse({'success': False, 'message': 'Missing required parameters'})
        
        try:
            order = testOrder.objects.get(id=order_id)
        except testOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        
        if action == 'retry':
            # Reset payment status for retry
            order.payment_status = 'pending'
            order.save()
            
            # Send retry email to patient
            if order.user and order.user.email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject='Payment Retry - Lab Test Order',
                    message=f'''
Dear {order.user.first_name} {order.user.last_name},

Your lab test order payment failed, but you can retry the payment now.

Order ID: #{order_id}
Amount: ₹{order.final_bill if hasattr(order, 'final_bill') else order.total_amount}

Please log into your patient dashboard to retry the payment for your lab tests.

Our lab technician team is ready to collect your samples once payment is completed.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                    fail_silently=True,
                )
            
            message = 'Payment retry enabled. Patient has been notified via email.'
            
        elif action == 'convert_to_cod':
            # Convert to cash on delivery
            order.payment_status = 'cod_pending'
            order.save()
            
            # Send COD conversion email
            if order.user and order.user.email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject='Payment Method Changed to Cash on Delivery',
                    message=f'''
Dear {order.user.first_name} {order.user.last_name},

Your lab test order has been converted to Cash on Delivery (COD) payment method.

Order ID: #{order_id}
Amount: ₹{order.final_bill if hasattr(order, 'final_bill') else order.total_amount}
Payment Method: Cash on Delivery

Our lab technician will collect the payment in cash when collecting your samples. Please keep the exact amount ready.

You will receive a call from our team to schedule the sample collection.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                    fail_silently=True,
                )
            
            message = 'Order converted to COD. Patient will pay during sample collection.'
            
        elif action == 'cancel':
            # Cancel the order
            order.payment_status = 'cancelled'
            order.ordered = False
            order.save()
            
            # Send cancellation email
            if order.user and order.user.email:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject='Lab Test Order Cancelled',
                    message=f'''
Dear {order.user.first_name} {order.user.last_name},

Your lab test order has been cancelled due to payment issues.

Order ID: #{order_id}
Cancellation Date: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

If you still need these tests, please create a new order through your patient dashboard or contact our support team.

We apologize for any inconvenience caused.

Best regards,
Mahima Medicare Laboratory Team
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[order.user.email],
                    fail_silently=True,
                )
            
            message = 'Order cancelled successfully. Patient has been notified.'
            
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action specified'})
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error handling payment failure: {str(e)}'})


# PRESCRIPTION UPLOAD MANAGEMENT FUNCTIONS

@csrf_exempt
@login_required(login_url='admin_login')
def review_prescription_upload(request, upload_id):
    """Review and process prescription upload"""
    if not request.user.is_pharmacist:
        return redirect('admin-logout')
    
    from pharmacy.models import PrescriptionUpload, Medicine, PrescriptionMedicine
    from django.utils import timezone
    
    pharmacist = Pharmacist.objects.get(user=request.user)
    prescription = get_object_or_404(PrescriptionUpload, upload_id=upload_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        pharmacist_notes = request.POST.get('pharmacist_notes', '')
        
        if action == 'approve':
            # Calculate total cost from added medicines
            total_cost = sum(med.total_price or 0 for med in prescription.medicines.all())
            
            # Add delivery charges if applicable
            if prescription.delivery_method == 'delivery':
                total_cost += 40  # Delivery charge
            
            prescription.status = 'approved'
            prescription.pharmacist = pharmacist
            prescription.pharmacist_notes = pharmacist_notes
            prescription.estimated_cost = total_cost
            prescription.reviewed_at = timezone.now()
            prescription.save()
            
            messages.success(request, f'Prescription #{upload_id} approved successfully!')
            
            # Send email notification
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                if prescription.patient.email:
                    send_mail(
                        'Prescription Approved - Mahima Medicare',
                        f'Your prescription #{upload_id} has been approved. Total cost: ₹{total_cost}. You can now proceed with payment.',
                        settings.EMAIL_HOST_USER,
                        [prescription.patient.email],
                        fail_silently=True
                    )
            except Exception:
                pass
                
        elif action == 'reject':
            prescription.status = 'rejected'
            prescription.pharmacist = pharmacist
            prescription.pharmacist_notes = pharmacist_notes
            prescription.reviewed_at = timezone.now()
            prescription.save()
            
            messages.info(request, f'Prescription #{upload_id} rejected.')
            
            # Send rejection notification
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                if prescription.patient.email:
                    send_mail(
                        'Prescription Review - Mahima Medicare',
                        f'Your prescription #{upload_id} has been reviewed. Please check the pharmacist notes and contact us for assistance.',
                        settings.EMAIL_HOST_USER,
                        [prescription.patient.email],
                        fail_silently=True
                    )
            except Exception:
                pass
        
        return redirect('pharmacist-order-management')
    
    # GET request - show review form
    available_medicines = Medicine.objects.filter(quantity__gt=0).order_by('name')
    
    context = {
        'prescription': prescription,
        'pharmacist': pharmacist,
        'medicines': available_medicines,
    }
    return render(request, 'hospital_admin/review-prescription-upload.html', context)


@csrf_exempt  
@login_required(login_url='admin_login')
def add_medicine_to_prescription(request, upload_id):
    """Add or update medicine in prescription"""
    if not request.user.is_pharmacist:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    from pharmacy.models import PrescriptionUpload, Medicine, PrescriptionMedicine
    
    if request.method == 'POST':
        try:
            prescription = get_object_or_404(PrescriptionUpload, upload_id=upload_id)
            medicine_id = request.POST.get('medicine_id')
            quantity = int(request.POST.get('quantity', 1))
            dosage = request.POST.get('dosage', '')
            days = request.POST.get('days')
            
            medicine = get_object_or_404(Medicine, serial_number=medicine_id)
            
            # Create or update prescription medicine
            prescription_med, created = PrescriptionMedicine.objects.get_or_create(
                prescription_upload=prescription,
                medicine=medicine,
                defaults={
                    'quantity': quantity,
                    'dosage': dosage,
                    'days': int(days) if days else None,
                    'unit_price': medicine.price,
                    'total_price': medicine.price * quantity
                }
            )
            
            if not created:
                prescription_med.quantity = quantity
                prescription_med.dosage = dosage
                prescription_med.days = int(days) if days else None
                prescription_med.unit_price = medicine.price
                prescription_med.total_price = medicine.price * quantity
                prescription_med.save()
            
            # Recalculate prescription estimated cost
            from decimal import Decimal
            prescription_medicines = PrescriptionMedicine.objects.filter(prescription_upload=prescription)
            total_cost = sum(Decimal(str(med.total_price or 0)) for med in prescription_medicines)
            prescription.estimated_cost = total_cost
            prescription.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Added {medicine.name} to prescription',
                'medicine_name': medicine.name,
                'quantity': quantity,
                'price': float(medicine.price * quantity),
                'estimated_cost': float(total_cost),
                'medicine_count': prescription_medicines.count()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
@login_required(login_url='admin_login')
def remove_medicine_from_prescription(request, upload_id, medicine_id):
    """Remove medicine from prescription"""
    if not request.user.is_pharmacist:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    from pharmacy.models import PrescriptionUpload, PrescriptionMedicine
    
    try:
        prescription = get_object_or_404(PrescriptionUpload, upload_id=upload_id)
        prescription_med = get_object_or_404(
            PrescriptionMedicine, 
            prescription_upload=prescription,
            medicine__serial_number=medicine_id
        )
        
        medicine_name = prescription_med.medicine.name
        prescription_med.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Removed {medicine_name} from prescription'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ==================== HOME SAMPLE COLLECTION MANAGEMENT ====================

@login_required(login_url='admin-login')
def home_collection_dashboard(request):
    '''Comprehensive home sample collection management dashboard'''
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    from doctor.models import testOrder
    from hospital_admin.models import Clinical_Laboratory_Technician
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get today's date
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Home collection orders
    home_orders = testOrder.objects.filter(
        collection_type='home',
        ordered=True
    ).select_related('user').order_by('-created')
    
    # Statistics
    stats = {
        'total_home_orders': home_orders.count(),
        'pending_collections': home_orders.filter(collection_status='pending').count(),
        'scheduled_today': home_orders.filter(
            collection_status='scheduled',
            preferred_collection_date=today
        ).count(),
        'scheduled_tomorrow': home_orders.filter(
            collection_status='scheduled',
            preferred_collection_date=tomorrow
        ).count(),
        'in_progress': home_orders.filter(collection_status='in_progress').count(),
        'completed_today': home_orders.filter(
            collection_status='collected',
            preferred_collection_date=today
        ).count(),
        'cod_pending': home_orders.filter(payment_status='cod_pending').count(),
        'cod_paid': home_orders.filter(payment_status='paid').count(),
    }
    
    # Today's scheduled collections
    todays_collections = home_orders.filter(
        collection_status__in=['scheduled', 'in_progress'],
        preferred_collection_date=today
    )
    
    # Urgent collections (overdue)
    urgent_collections = home_orders.filter(
        collection_status__in=['pending', 'scheduled'],
        preferred_collection_date__lt=today
    )
    
    # Upcoming collections (next 3 days)
    upcoming_collections = home_orders.filter(
        collection_status='scheduled',
        preferred_collection_date__gt=today,
        preferred_collection_date__lte=today + timedelta(days=3)
    )
    
    context = {
        'stats': stats,
        'todays_collections': todays_collections,
        'urgent_collections': urgent_collections,
        'upcoming_collections': upcoming_collections,
        'lab_worker': lab_worker,
        'today': today,
    }
    
    return render(request, 'hospital_admin/home-collection-dashboard.html', context)


@login_required(login_url='admin-login')
def home_collection_schedule(request):
    '''Schedule and manage home collections'''
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    from doctor.models import testOrder
    
    # Get filter parameters
    date_filter = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    orders = testOrder.objects.filter(
        collection_type='home',
        ordered=True
    ).select_related('user').order_by('preferred_collection_date', 'preferred_collection_time')
    
    # Apply filters
    if date_filter:
        orders = orders.filter(preferred_collection_date=date_filter)
    if status_filter:
        orders = orders.filter(collection_status=status_filter)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_orders = paginator.get_page(page_number)
    
    context = {
        'orders': page_orders,
        'date_filter': date_filter,
        'status_filter': status_filter,
        'today': timezone.now().date(),
    }
    
    return render(request, 'hospital_admin/home-collection-schedule.html', context)


@login_required(login_url='admin-login')
def update_collection_status(request, order_id):
    '''Update home collection status'''
    if not request.user.is_labworker:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    from doctor.models import testOrder
    
    if request.method == 'POST':
        try:
            order = get_object_or_404(testOrder, id=order_id, collection_type='home')
            new_status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            if new_status in ['pending', 'scheduled', 'in_progress', 'collected', 'completed', 'cancelled']:
                order.collection_status = new_status
                order.save()
                
                # If collected, also update payment status for COD orders
                if new_status == 'collected' and order.payment_status == 'cod_pending':
                    # This will be updated when payment is received
                    pass
                
                messages.success(request, f'Collection status updated to {new_status}')
                return JsonResponse({'success': True, 'message': 'Status updated successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid status'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='admin-login') 
def process_cod_collection_payment(request, order_id):
    '''Process COD payment for home collection'''
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    from doctor.models import testOrder
    from razorpay_payment.models import Payment
    
    order = get_object_or_404(testOrder, id=order_id, collection_type='home')
    
    if request.method == 'POST':
        try:
            amount_received = Decimal(request.POST.get('amount_received', 0))
            payment_method = request.POST.get('payment_method', 'cash')
            
            if amount_received >= order.final_bill:
                # Create payment record
                payment = Payment.objects.create(
                    user=order.user,
                    payment_id=f'COD_HC_{order.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    order_id=str(order.id),
                    signature=f'home_collection_cod_{order.id}',
                    amount=float(order.final_bill),
                    status='paid'
                )
                
                # Update order
                order.payment_status = 'paid'
                order.collection_status = 'completed'
                order.save()
                
                # Update all associated test items
                for cart_item in order.orderitems.all():
                    cart_item.item.test_info_pay_status = 'paid'
                    cart_item.item.test_status = 'collected'
                    cart_item.item.save()
                
                messages.success(request, f'Payment of ₹{amount_received} received successfully!')
                return redirect('home-collection-dashboard')
            else:
                messages.error(request, f'Amount received (₹{amount_received}) is less than required (₹{order.final_bill})')
                
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    context = {
        'order': order,
        'required_amount': order.final_bill,
    }
    
    return render(request, 'hospital_admin/process-cod-collection.html', context)


@login_required(login_url='admin-login')
def home_collection_details(request, order_id):
    '''View detailed information about a home collection order'''
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    from doctor.models import testOrder
    
    order = get_object_or_404(testOrder, id=order_id, collection_type='home')
    
    # Get patient information
    patient_info = {
        'name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username,
        'email': order.user.email,
        'phone': getattr(order.user, 'phone', 'N/A'),
    }
    
    # Get test details
    test_items = order.orderitems.all()
    
    context = {
        'order': order,
        'patient_info': patient_info,
        'test_items': test_items,
        'collection_fee': order.home_collection_charge,
        'total_amount': order.final_bill,
    }
    
    return render(request, 'hospital_admin/home-collection-details.html', context)


@login_required(login_url='admin-login')
def print_collection_receipt(request, order_id):
    '''Generate printable receipt for home collection'''
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    from doctor.models import testOrder
    
    order = get_object_or_404(testOrder, id=order_id, collection_type='home')
    
    context = {
        'order': order,
        'patient_name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.username,
        'test_items': order.orderitems.all(),
        'print_date': timezone.now(),
    }
    
    return render(request, 'hospital_admin/collection-receipt.html', context)
