import email
from email.mime import image
from multiprocessing import context
from unicodedata import name
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from hospital.models import Hospital_Information, User, Patient
from django.db.models import Q
from pharmacy.models import Medicine, Pharmacist
from pharmacy.forms import MedicineForm
from doctor.models import Doctor_Information, Prescription, Prescription_test, Report, Appointment, Experience , Education,Specimen,Test
from pharmacy.models import Order, Cart
from .forms import AdminUserCreationForm, LabWorkerCreationForm, EditHospitalForm, EditEmergencyForm,AdminForm , PharmacistCreationForm 

from .models import Admin_Information,specialization,service,hospital_department, Clinical_Laboratory_Technician, Test_Information
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
    # return render(request, 'hospital_admin/admin-dashboard.html', context)

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
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_hospital_admin:
                messages.success(request, 'User logged in')
                return redirect('dashboard')
            elif user.is_labworker:
                messages.success(request, 'User logged in')
                return redirect('labworker-dashboard')
            elif user.is_pharmacist:
                messages.success(request, 'User logged in')
                return redirect('pharmacist-dashboard')
            else:
                return redirect('admin-logout')
        else:
            messages.error(request, 'Invalid username or password')
        

    return render(request, 'hospital_admin/login.html')


@csrf_exempt
def admin_register(request):
    page = 'hospital_admin/register'
    form = AdminUserCreationForm()

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            # commit=False --> don't save to database yet (we have a chance to modify object)
            user = form.save(commit=False)
            user.is_hospital_admin = True
            user.save()

            messages.success(request, 'User account was created!')
            
            # After user is created, we can log them in
            #login(request, user)
            return redirect('admin_login')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'hospital_admin/register.html', context)

@csrf_exempt
@login_required(login_url='admin_login')
def admin_forgot_password(request):
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
    if request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
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
    if  request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)

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
        weight = request.POST.get('weight', '').strip()
        quantity_str = request.POST.get('quantity', '').strip()
        price_str = request.POST.get('price', '').strip()

        requirement_type = request.POST.get('requirement_type', '')
        category_type = request.POST.get('category_type', '')
        medicine_type = request.POST.get('medicine_type', '')
        description = request.POST.get('description', '').strip()
        featured_image = request.FILES.get('featured_image')
        expiry_date_str = request.POST.get('expiry_date', '').strip()

        # Parse expiry_date
        from datetime import datetime
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append('Invalid expiry date format.')

        # Initialize error flag
        errors = []

        # Validate required fields
        if not name:
            errors.append('Medicine name is required.')
        
        if not weight:
            errors.append('Weight is required.')
        
        # Validate quantity
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                errors.append('Quantity must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid number.')
        
        # Validate price
        try:
            price = float(price_str)
            if price < 0:
                errors.append('Price must be a positive number.')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number.')

        # If there are errors, return to form with messages
        if errors:
            for error in errors:
                messages.error(request, error)
            ctx = {'admin': user}
            if pharmacist_ctx:
                ctx['pharmacist'] = pharmacist_ctx
            return render(request, 'hospital_admin/add-medicine.html', ctx)

        # Generate unique medicine ID
        medicine_id = f"#M-{str(uuid.uuid4())[:8].upper()}"

        try:
            # Create medicine instance
            medicine = Medicine(
                name=name,
                weight=weight,
                quantity=quantity,
                price=price,
                Prescription_reqiuired=requirement_type,
                medicine_category=category_type,
                medicine_type=medicine_type,
                description=description,
                featured_image=featured_image or 'medicines/default.png',
                stock_quantity=quantity,
                medicine_id=medicine_id,
                expiry_date=expiry_date
            )
            # Save to database
            medicine.save()
            # Success message and redirect
            messages.success(request, f'Medicine "{name}" added successfully!')
            return redirect('medicine-list')
        except Exception as e:
            messages.error(request, f'Error adding medicine: {str(e)}')
            ctx = {'admin': user}
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
    if request.user.is_pharmacist:
        user = Pharmacist.objects.get(user=request.user)
    elif request.user.is_hospital_admin:
        user = Admin_Information.objects.get(user=request.user)
    
    medicine = get_object_or_404(Medicine, serial_number=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        
        if form.is_valid():
            medicine = form.save(commit=False)
            # Only update stock_quantity if it was explicitly provided in the form
            # Otherwise, keep the existing stock_quantity value
            if 'stock_quantity' in request.POST and request.POST['stock_quantity']:
                try:
                    medicine.stock_quantity = int(request.POST['stock_quantity'])
                except ValueError:
                    pass  # Keep existing value if conversion fails
            medicine.save()
            messages.success(request, f'Medicine "{medicine.name}" updated successfully!')
            return redirect('medicine-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'hospital_admin/edit-medicine.html', {'form': form, 'medicine': medicine, 'admin': user})


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
                # form.save(), commit=False --> don't save to database yet (we have a chance to modify object)
                user = form.save(commit=False)
                user.is_labworker = True
                user.save()

                messages.success(request, 'Clinical Laboratory Technician account was created!')

                # After user is created, we can log them in
                #login(request, user)
                return redirect('lab-worker-list')
            else:
                messages.error(request, 'An error has occurred during registration')
    
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
    if request.user.is_authenticated:
        if request.user.is_labworker:
            # Check if the lab worker is also an admin and redirect to admin dashboard
            if request.user.is_hospital_admin:
                return redirect('admin-dashboard')
            
            # Set the number of lab technicians to 4
            total_labworker_count = 4
            lab_workers = Clinical_Laboratory_Technician.objects.all()  # Keep this for any other logic if needed
            doctor = Doctor_Information.objects.all()
            total_patient_count = Patient.objects.count()
            available_tests = Test_Information.objects.all()

            context = {
                'doctor': doctor,
                'lab_workers': lab_workers,
                'total_patient_count': total_patient_count,
                'available_tests': available_tests,
                'total_labworker_count': total_labworker_count
            }
            return render(request, 'hospital_admin/labworker-dashboard.html', context)

@csrf_exempt
@login_required(login_url='admin-login')
def mypatient_list(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            
            # Get filter parameter
            show_filter = request.GET.get('show', 'pending')
            
            if show_filter == 'all':
                # Show all patients
                patient = Patient.objects.all()
            elif show_filter == 'completed':
                # Show patients with completed reports
                completed_patient_ids = Report.objects.filter(
                    status__in=['completed', 'delivered']
                ).values_list('patient_id', flat=True).distinct()
                patient = Patient.objects.filter(patient_id__in=completed_patient_ids)
            else:
                # Default: Show patients who need reports (pending or no reports)
                completed_patient_ids = Report.objects.filter(
                    status__in=['completed', 'delivered']
                ).values_list('patient_id', flat=True).distinct()
                patient = Patient.objects.exclude(patient_id__in=completed_patient_ids)
            
            # Get report status for each patient
            patients_with_reports = []
            for p in patient:
                latest_report = Report.objects.filter(patient=p).order_by('-uploaded_at').first()
                p.latest_report = latest_report
                patients_with_reports.append(p)
            
            context = {
                'patient': patients_with_reports,
                'lab_workers': lab_workers,
                'show_filter': show_filter
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
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
        test = Test_Information.objects.all()
        context = {'test':test,'lab_workers':lab_workers}
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
            
            # Prepare JSON data for JavaScript charts
            import json
            medicines_for_chart = Medicine.objects.all()[:20]  # Top 20 for chart
            medicines_json = json.dumps([
                {
                    'name': medicine.name,
                    'stock': medicine.quantity if medicine.quantity else 0
                }
                for medicine in medicines_for_chart
            ])
            
            context = {'pharmacist':pharmacist, 'medicine':page_obj,
                       'medicines': medicine_list,  # All medicines for template
                       'medicines_json': medicines_json,  # JSON data for charts
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

    # Each purchased cart item as row history
    purchased_items = (
        Cart.objects.filter(purchased=True)
        .select_related('item', 'user')
        .order_by('-updated')
    )

    context = {
        'purchased_items': purchased_items,
        'pharmacist': pharmacist,
    }
    return render(request, 'hospital_admin/pharmacist-purchase-history.html', context)


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

                    Medicine.objects.create(
                        name=name,
                        weight=weight,
                        quantity=quantity,
                        stock_quantity=quantity,
                        price=price,
                        description=description,
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
    """Enhanced lab dashboard with comprehensive statistics and tracking"""
    if not request.user.is_labworker:
        return redirect('admin-logout')
    
    lab_worker = Clinical_Laboratory_Technician.objects.get(user=request.user)
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Report statistics
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    processing_reports = Report.objects.filter(status='processing').count()
    completed_reports = Report.objects.filter(status='completed').count()
    delivered_reports = Report.objects.filter(status='delivered').count()
    
    # My assigned reports
    my_reports = Report.objects.filter(assigned_technician=lab_worker)
    my_pending = my_reports.filter(status__in=['pending', 'collected']).count()
    my_processing = my_reports.filter(status='processing').count()
    my_completed = my_reports.filter(status='completed').count()
    
    # Recent activity
    recent_reports = Report.objects.filter(
        assigned_technician=lab_worker
    ).order_by('-updated_at')[:10]
    
    # Urgent reports
    urgent_reports = Report.objects.filter(
        priority__in=['urgent', 'stat'],
        status__in=['pending', 'collected', 'processing']
    ).order_by('priority', 'uploaded_at')[:5]
    
    # Weekly statistics
    weekly_completed = Report.objects.filter(
        status='completed',
        delivery_date__gte=week_ago,
        assigned_technician=lab_worker
    ).count()
    
    # Test orders pending assignment
    unassigned_reports = Report.objects.filter(
        assigned_technician__isnull=True,
        status='pending'
    ).count()
    
    context = {
        'lab_worker': lab_worker,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'processing_reports': processing_reports,
        'completed_reports': completed_reports,
        'delivered_reports': delivered_reports,
        'my_pending': my_pending,
        'my_processing': my_processing,
        'my_completed': my_completed,
        'recent_reports': recent_reports,
        'urgent_reports': urgent_reports,
        'weekly_completed': weekly_completed,
        'unassigned_reports': unassigned_reports,
    }
    
    return render(request, 'hospital_admin/lab-dashboard.html', context)


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
