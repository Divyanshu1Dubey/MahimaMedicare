import email
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, PatientForm, PasswordResetForm
from hospital.models import Hospital_Information, User, Patient 
from doctor.models import Test, testCart, testOrder
from hospital_admin.models import hospital_department, specialization, service, Test_Information
from django.views.decorators.cache import cache_control
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import searchDoctors, searchHospitals, searchDepartmentDoctors, paginateHospitals
from .models import Patient, User
from doctor.models import Doctor_Information, Appointment,Report, Specimen, Test, Prescription, Prescription_medicine, Prescription_test
from django.db.models import Q, Count
import re
from io import BytesIO
from urllib import response
from django.core.mail import BadHeaderError, send_mail
import ssl
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from .forms import DoctorRegistrationForm


# Create your views here.
@csrf_exempt
def hospital_home(request):
    # .order_by('-created_at')[:6]
    doctors = Doctor_Information.objects.filter(register_status='Accepted')
    hospitals = Hospital_Information.objects.all()
    context = {'doctors': doctors, 'hospitals': hospitals} 
    return render(request, 'index-2.html', context)

@csrf_exempt
@login_required(login_url="login")
def change_password(request,pk):
    patient = Patient.objects.get(user_id=pk)
    context={"patient":patient}
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("patient-dashboard")
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'change-password.html',context)


def add_billing(request):
    return render(request, 'add-billing.html')

def appointments(request):
    return render(request, 'appointments.html')

def edit_billing(request):
    return render(request, 'edit-billing.html')

def edit_prescription(request):
    return render(request, 'edit-prescription.html')

# def forgot_password(request):
#     return render(request, 'forgot-password.html')

@csrf_exempt
def resetPassword(request):
    form = PasswordResetForm()

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_email = user.email
       
            subject = "Password Reset Requested"
            # email_template_name = "password_reset_email.txt"
            values = {
				"email":user.email,
				'domain':'127.0.0.1:8000',
				'site_name': 'Website',
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				"user": user,
				'token': default_token_generator.make_token(user),
				'protocol': 'http',
			}

            html_message = render_to_string('mail_template.html', {'values': values})
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(subject, plain_message, 'admin@example.com',  [user.email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("password_reset_done")

    context = {'form': form}
    return render(request, 'reset_password.html', context)
    
    
def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def about_us(request):
    return render(request, 'about-us.html')

@csrf_exempt
@login_required(login_url="login")
def chat(request, pk):
    patient = Patient.objects.get(user_id=pk)
    doctors = Doctor_Information.objects.all()

    context = {'patient': patient, 'doctors': doctors}
    return render(request, 'chat.html', context)

@csrf_exempt
@login_required(login_url="login")
def chat_doctor(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patients = Patient.objects.all()
        
    context = {'patients': patients, 'doctor': doctor}
    return render(request, 'chat-doctor.html', context)

@csrf_exempt     
@login_required(login_url="login")
def pharmacy_shop(request):
    return render(request, 'pharmacy/shop.html')

@csrf_exempt
def login_user(request):
    page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'patient-login.html')
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
            if request.user.is_patient:   
                messages.success(request, 'User Logged in Successfully')    
                return redirect('patient-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Patient')
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'patient-login.html')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutUser(request):
    logout(request)
    messages.success(request, 'User Logged out')
    return redirect('login')

@csrf_exempt
def patient_register(request):
    page = 'patient-register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            user = form.save(commit=False) # commit=False --> don't save to database yet (we have a chance to modify object)
            user.is_patient = True
            # user.username = user.username.lower()  # lowercase username
            user.save()
            messages.success(request, 'Patient account was created!')

            # After user is created, we can log them in --> login(request, user)
            return redirect('login')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'patient-register.html', context)

@csrf_exempt
@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def patient_dashboard(request):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        
        # Enhanced data collection
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Reports with status breakdown
        reports = Report.objects.filter(patient=patient).order_by('-uploaded_at')
        reports_pending = reports.filter(status='pending').count()
        reports_processing = reports.filter(status='processing').count()
        reports_completed = reports.filter(status='completed').count()
        reports_delivered = reports.filter(status='delivered').count()
        
        # Recent reports (last 30 days)
        recent_reports = reports.filter(
            uploaded_at__gte=timezone.now() - timedelta(days=30)
        )
        
        # Prescriptions with better filtering
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescription_id')
        recent_prescriptions = prescriptions.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ) if hasattr(Prescription, 'created_at') else prescriptions[:5]
        
        # Appointments with status breakdown
        all_appointments = Appointment.objects.filter(patient=patient)
        upcoming_appointments = all_appointments.filter(
            Q(appointment_status='pending') | Q(appointment_status='confirmed')
        ).order_by('date')
        
        completed_appointments = all_appointments.filter(
            appointment_status='completed'
        ).count()
        
        # Get Razorpay payments with better filtering
        from razorpay_payment.models import RazorpayPayment
        payments = RazorpayPayment.objects.filter(
            patient=patient,
            status='captured'
        ).order_by('-created_at')
        
        # Payment statistics
        total_payments = payments.count()
        total_amount_paid = sum([payment.amount for payment in payments])
        recent_payments = payments[:5]  # Last 5 payments
        
        # Health summary
        health_summary = {
            'total_reports': reports.count(),
            'total_prescriptions': prescriptions.count(),
            'total_appointments': all_appointments.count(),
            'completed_appointments': completed_appointments,
            'total_payments': total_payments,
            'total_amount_paid': total_amount_paid,
        }
        
        # Urgent notifications
        urgent_notifications = []
        
        # Check for pending reports
        if reports_pending > 0:
            urgent_notifications.append({
                'type': 'warning',
                'icon': 'fas fa-clock',
                'message': f'You have {reports_pending} pending lab report(s)',
                'action_url': '#reports-section',
                'action_text': 'View Reports'
            })
        
        # Check for ready reports
        ready_reports = reports.filter(status='completed')
        if ready_reports.exists():
            urgent_notifications.append({
                'type': 'success',
                'icon': 'fas fa-file-medical',
                'message': f'{ready_reports.count()} new lab report(s) ready for download',
                'action_url': '#reports-section',
                'action_text': 'Download Reports'
            })
        
        # Check for upcoming appointments
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        upcoming_soon = upcoming_appointments.filter(date=tomorrow)
        if upcoming_soon.exists():
            urgent_notifications.append({
                'type': 'info',
                'icon': 'fas fa-calendar-check',
                'message': f'You have {upcoming_soon.count()} appointment(s) tomorrow',
                'action_url': '#appointments-section',
                'action_text': 'View Appointments'
            })

        context = {
            'patient': patient,
            'appointments': upcoming_appointments,
            'payments': recent_payments,
            'report': reports,
            'prescription': recent_prescriptions,
            'health_summary': health_summary,
            'reports_stats': {
                'pending': reports_pending,
                'processing': reports_processing,
                'completed': reports_completed,
                'delivered': reports_delivered,
            },
            'recent_reports': recent_reports,
            'urgent_notifications': urgent_notifications,
            'total_amount_paid': total_amount_paid,
        }
    else:
        return redirect('logout')
        
    return render(request, 'patient-dashboard.html', context)


@csrf_exempt
@login_required(login_url='login')
def download_report_pdf(request, report_id):
    from doctor.models import Report
    from django.shortcuts import get_object_or_404
    
    report = get_object_or_404(Report, report_id=report_id)
    
    # Check permissions - patient can only download their own reports
    if hasattr(request.user, 'patient') and request.user.patient == report.patient:
        pass  # Patient can download their own reports
    elif request.user.is_labworker:
        pass  # Lab workers can download any report
    else:
        messages.error(request, 'You do not have permission to access this report.')
        return redirect('patient-dashboard')
    
    if not report.report_pdf:
        messages.error(request, 'No PDF report available for download.')
        return redirect('patient-dashboard')
    
    from django.http import FileResponse
    
    try:
        response = FileResponse(
            report.report_pdf.open('rb'),
            as_attachment=True,
            filename=f'lab_report_{report.report_id}_{report.patient.username}.pdf'
        )
        return response
    except Exception as e:
        messages.error(request, 'Error downloading report. Please try again.')
        return redirect('patient-dashboard')


# def profile_settings(request):
#     if request.user.is_patient:
#         # patient = Patient.objects.get(user_id=pk)
#         patient = Patient.objects.get(user=request.user)
#         form = PatientForm(instance=patient)  

#         if request.method == 'POST':
#             form = PatientForm(request.POST, request.FILES,instance=patient)  
#             if form.is_valid():
#                 form.save()
#                 return redirect('patient-dashboard')
#             else:
#                 form = PatientForm()
#     else:
#         redirect('logout')

#     context = {'patient': patient, 'form': form}
#     return render(request, 'profile-settings.html', context)

@csrf_exempt
@login_required(login_url="login")
def profile_settings(request):
    if request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        old_featured_image = patient.featured_image
        
        if request.method == 'GET':
            context = {'patient': patient}
            return render(request, 'profile-settings.html', context)
        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image
                
            name = request.POST.get('name')
            dob = request.POST.get('dob')
            age = request.POST.get('age')
            blood_group = request.POST.get('blood_group')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            nid = request.POST.get('nid')
            history = request.POST.get('history')
            
            patient.name = name
            patient.age = age
            patient.phone_number = phone_number
            patient.address = address
            patient.blood_group = blood_group
            patient.history = history
            patient.dob = dob
            patient.nid = nid
            patient.featured_image = featured_image
            
            patient.save()
            
            messages.success(request, 'Profile Settings Changed!')
            
            return redirect('patient-dashboard')
    else:
        redirect('logout')  
        
@csrf_exempt
@login_required(login_url="login")
def search(request):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        doctors = Doctor_Information.objects.filter(register_status='Accepted')
        
        doctors, search_query = searchDoctors(request)
        context = {'patient': patient, 'doctors': doctors, 'search_query': search_query}
        return render(request, 'search.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')    
    

def checkout_payment(request):
    return render(request, 'checkout.html')

@csrf_exempt
@login_required(login_url="login")
def multiple_hospital(request):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            # PAGINATION ADDED TO MULTIPLE HOSPITALS
            custom_range, hospitals = paginateHospitals(request, hospitals, 3)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'search_query': search_query, 'custom_range': custom_range}
            return render(request, 'multiple-hospital.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'search_query': search_query}
            return render(request, 'multiple-hospital.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
@csrf_exempt    
@login_required(login_url="login")
def hospital_profile(request, pk):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
        
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            # department_list = None
            # for d in departments:
            #     vald = d.hospital_department_name
            #     vald = re.sub("'", "", vald)
            #     vald = vald.replace("[", "")
            #     vald = vald.replace("]", "")
            #     vald = vald.replace(",", "")
            #     department_list = vald.split()
            
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
        
        elif request.user.is_doctor:
           
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
    
def data_table(request):
    return render(request, 'data-table.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_department_list(request, pk):
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_list(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        doctors = Doctor_Information.objects.filter(department_name=departments)
        
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'patient': patient, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)

    elif request.user.is_authenticated and request.user.is_doctor:
        # patient = Patient.objects.get(user_id=pk)
        
        doctor = Doctor_Information.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        
        doctors = Doctor_Information.objects.filter(department_name=departments)
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'doctor':doctor, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')   
    


@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_register(request, pk):
    if not request.user.is_doctor:
        logout(request)
        messages.info(request, 'Not Authorized. Please log in as a doctor.')
        return render(request, 'doctor-login.html')

    doctor = get_object_or_404(Doctor_Information, user=request.user)
    hospital = get_object_or_404(Hospital_Information, hospital_id=pk)
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES, hospital_id=pk)
        if form.is_valid():
            department_chosen = form.cleaned_data['department']
            specialization_chosen = form.cleaned_data['specialization'] 
            certificate = form.cleaned_data['certificate_image']

            doctor.department_name = department_chosen
            doctor.specialization = specialization_chosen
            doctor.register_status = 'Pending'
            if certificate:
                doctor.certificate_image = certificate
            
            doctor.save()
            messages.success(request, 'Your registration request has been sent successfully!')
            return redirect('doctor-dashboard')

    else:
        form = DoctorRegistrationForm(hospital_id=pk)

    context = {
        'form': form,
        'doctor': doctor,
        'hospitals': hospital,
    }
    return render(request, 'hospital-doctor-register.html', context)
    
   
def testing(request):
    # hospitals = Hospital_Information.objects.get(hospital_id=1)
    test = "test"
    context = {'test': test}
    return render(request, 'testing.html', context)

@csrf_exempt
@login_required(login_url="login")
def view_report(request,pk):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        report = Report.objects.filter(report_id=pk)
        specimen = Specimen.objects.filter(report__in=report)
        test = Test.objects.filter(report__in=report)

        # current_date = datetime.date.today()
        context = {'patient':patient,'report':report,'test':test,'specimen':specimen}
        return render(request, 'view-report.html',context)
    else:
        redirect('logout') 



@csrf_exempt
@login_required(login_url="login")
def test_single(request,pk):
     if request.user.is_authenticated and request.user.is_patient:
         
        patient = Patient.objects.get(user=request.user)
        Perscription_test = Perscription_test.objects.get(test_id=pk)
        carts = testCart.objects.filter(user=request.user, purchased=False)
        
        context = {'patient': patient, 'carts': carts, 'Perscription_test': Perscription_test}
        return render(request, 'test-cart.html',context)
     else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')  

@csrf_exempt
@login_required(login_url="login")
def test_add_to_cart(request, prescription_id, test_info_id):
    if request.user.is_authenticated and request.user.is_patient:
        # Get patient
        patient = Patient.objects.get(user=request.user)

        # Get the Prescription_test item
        item = get_object_or_404(Prescription_test, test_info_id=test_info_id, prescription_id=prescription_id)

        # Create or get the testCart entry
        cart_item, created = testCart.objects.get_or_create(
            item=item,
            user=request.user,
            purchased=False
        )

        # Get or create a testOrder specifically for this prescription
        # One Order per Prescription approach
        order_qs = testOrder.objects.filter(
            user=request.user, 
            ordered=False,
            orderitems__item__prescription__prescription_id=prescription_id
        ).distinct()
        
        if order_qs.exists():
            order = order_qs.first()
        else:
            # Create a new testOrder for this prescription
            order = testOrder.objects.create(user=request.user, payment_status="pending")

        # Add cart item to order
        order.orderitems.add(cart_item)

        # Redirect back to prescription view
        return redirect("prescription-view", pk=prescription_id)

    logout(request)
    messages.info(request, 'Not Authorized')
    return redirect("patient-login")

@csrf_exempt
@login_required(login_url="login")
def test_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        prescription = Prescription.objects.filter(prescription_id=pk)
        patient = Patient.objects.get(user=request.user)
        prescription_test = Prescription_test.objects.all()
        
        # Get test carts for the current prescription
        test_carts = testCart.objects.filter(
            user=request.user, 
            purchased=False,
            item__prescription__prescription_id=pk
        )
        
        # Map test_info_id to test_name from Test_Information for cart items
        test_info_ids = [cart.item.test_info_id for cart in test_carts if cart.item.test_info_id]
        test_info_map = {}
        if test_info_ids:
            test_info_objs = Test_Information.objects.filter(test_id__in=test_info_ids)
            test_info_map = {str(ti.test_id): ti.test_name for ti in test_info_objs}
        
        # Attach actual test_name to each testCart item for template use
        for cart in test_carts:
            cart.item.actual_test_name = test_info_map.get(str(cart.item.test_info_id), cart.item.test_name)
        
        # Get test orders that contain items from the current prescription
        test_orders = testOrder.objects.filter(
            user=request.user, 
            ordered=False,
            orderitems__item__prescription__prescription_id=pk
        ).distinct()

        if test_carts.exists() and test_orders.exists():
            test_order = test_orders[0]
            
            # Calculate total amount with VAT using final_bill property
            total_amount = test_order.final_bill if hasattr(test_order, 'final_bill') else 0
            
            # Debug: print payment status
            print(f"Test order payment status: {test_order.payment_status}")
            print(f"Test order ID: {test_order.id}")
            print(f"Prescription ID: {pk}")
            print(f"Test carts count: {test_carts.count()}")
            print(f"Total amount: {total_amount}")

            context = {
                'test_carts': test_carts,
                'test_order': test_order,
                'patient': patient,
                'prescription_test': prescription_test,
                'prescription_id': pk,
                'total': total_amount,  # Add total to context
            }
            return render(request, 'test-cart.html', context)
        else:
            context = {'patient': patient, 'prescription_test': prescription_test}
            return render(request, 'prescription-view.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def test_remove_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # Get the testCart item by its ID
        cart_item = get_object_or_404(testCart, id=pk, user=request.user, purchased=False)

        # Remove from any active testOrder
        order_qs = testOrder.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs.first()
            if order.orderitems.filter(id=cart_item.id).exists():
                order.orderitems.remove(cart_item)

        # Delete the cart item
        cart_item.delete()

        # Redirect back to test cart page
        return redirect("test-cart", pk=cart_item.item.prescription.prescription_id)

    logout(request)
    messages.info(request, 'Not Authorized')
    return redirect("patient-login") 

@csrf_exempt
def prescription_view(request,pk):
      if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription = Prescription.objects.filter(prescription_id=pk)
        prescription_medicine = Prescription_medicine.objects.filter(prescription__in=prescription)
        prescription_test = Prescription_test.objects.filter(prescription__in=prescription)
        
        # Get test IDs that are already in the cart for this user
        cart_test_ids = list(testCart.objects.filter(
            user=request.user, 
            purchased=False,
            item__prescription__prescription_id=pk
        ).values_list('item__test_info_id', flat=True))
        
        # Map test_info_id to test_name from Test_Information
        test_info_ids = [pt.test_info_id for pt in prescription_test if pt.test_info_id]
        test_info_map = {}
        if test_info_ids:
            test_info_objs = Test_Information.objects.filter(test_id__in=test_info_ids)
            test_info_map = {str(ti.test_id): ti.test_name for ti in test_info_objs}
        
        # Attach actual test_name to each prescription_test object for template use
        for pt in prescription_test:
            pt.actual_test_name = test_info_map.get(str(pt.test_info_id), pt.test_name)
        
        context = {
            'patient': patient,
            'prescription': prescription,
            'prescription_test': prescription_test,
            'prescription_medicine': prescription_medicine,
            'cart_test_ids': cart_test_ids
        }
        return render(request, 'prescription-view.html',context)
      else:
         redirect('logout') 

@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pres_pdf=pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pres_pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pres_pdf")
    return None


# def prescription_pdf(request,pk):
#  if request.user.is_patient:
#     patient = Patient.objects.get(user=request.user)
#     prescription = Prescription.objects.get(prescription_id=pk)
#     perscription_medicine = Perscription_medicine.objects.filter(prescription=prescription)
#     perscription_test = Perscription_test.objects.filter(prescription=prescription)
#     current_date = datetime.date.today()
#     context={'patient':patient,'current_date' : current_date,'prescription':prescription,'perscription_test':perscription_test,'perscription_medicine':perscription_medicine}
#     pdf=render_to_pdf('prescription_pdf.html', context)
#     if pdf:
#         response=HttpResponse(pdf, content_type='application/pdf')
#         content="inline; filename=report.pdf"
#         # response['Content-Disposition']= content
#         return response
#     return HttpResponse("Not Found")

@csrf_exempt
def prescription_pdf(request,pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)
    prescription = Prescription.objects.get(prescription_id=pk)
    prescription_medicine = Prescription_medicine.objects.filter(prescription=prescription)
    prescription_test = Prescription_test.objects.filter(prescription=prescription)
    # current_date = datetime.date.today()
    context={'patient':patient,'prescription':prescription,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
    pres_pdf=render_to_pdf('prescription_pdf.html', context)
    if pres_pdf:
        response=HttpResponse(pres_pdf, content_type='application/pres_pdf')
        content="inline; filename=prescription.pdf"
        response['Content-Disposition']= content
        return response
    return HttpResponse("Not Found")

@csrf_exempt
@login_required(login_url="login")
def delete_prescription(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        prescription = Prescription.objects.get(prescription_id=pk)
        prescription.delete()
        messages.success(request, 'Prescription Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def delete_report(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        report = Report.objects.get(report_id=pk)
        report.delete()
        messages.success(request, 'Report Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.login_status = True
    user.save()

@csrf_exempt
@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.login_status = False
    user.save()
    