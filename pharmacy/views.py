import email
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator

from hospital.models import Patient
from pharmacy.models import Medicine, Cart, Order, PrescriptionUpload, PrescriptionMedicine
from .utils import searchMedicines
import requests
import base64


@csrf_exempt
@login_required(login_url="login")
def pharmacy_single_product(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'patient': patient, 'medicines': medicines, 'carts': carts, 'order': order, 'orders': orders}
        else:
            context = {'patient': patient, 'medicines': medicines, 'carts': carts, 'orders': orders}
        return render(request, 'pharmacy/product-single.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def pharmacy_shop(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        medicines, search_query = searchMedicines(request)
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)

        # Normalize category for JS filtering
        for med in medicines:
            raw_cat = med.medicine_category or ""
            normalized = (
                raw_cat.lower()
                .replace(" ", "")
                .replace("/", "")
                .replace("&", "")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(".", "")
            )
            # Map some common categories to tab values
            mapping = {
                "fever": "fever",
                "pain": "pain",
                "cough": "cough",
                "cold": "cold",
                "flu": "flu",
                "allergy": "allergy",
                "infection": "infection",
                "stomach": "stomach",
                "hypertension": "hypertension",
                "heart": "hypertension",
                "diabetes": "diabetes",
                "skin": "skin",
                "vitamins": "vitamins",
                "eyeearnose": "eye",
                "respiratoryasthmabronchitis": "respiratory",
                "urinary": "urinary",
                "firstaid": "firstaid",
            }
            med.normalized_category = mapping.get(normalized, normalized)

        # Find expiring medicines (within 30 days)
        expiring_medicines = [med for med in medicines if getattr(med, 'is_expiring_soon', False)]

        context = {
            'patient': patient,
            'medicines': medicines,
            'carts': carts,
            'orders': orders,
            'search_query': search_query,
            'expiring_medicines': expiring_medicines
        }
        if orders.exists():
            context['order'] = orders[0]

        return render(request, 'Pharmacy/shop.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')



@csrf_exempt
@login_required(login_url="login")
def cart_view(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        orders = Order.objects.filter(user=request.user, ordered=False)

        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'carts': carts, 'order': order, 'patient': patient}
            return render(request, 'Pharmacy/cart.html', context)
        else:
            messages.info(request, "Your cart is empty.")
            return redirect('pharmacy-shop')
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def add_to_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        
        # Check if item has sufficient unit quantity
        if item.quantity <= 0:
            messages.error(request, f"{item.name} is out of stock.")
            return redirect('pharmacy-shop')
        
        order_item, created = Cart.objects.get_or_create(item=item, user=request.user, purchased=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                # Check if adding one more would exceed unit quantity
                if order_item.quantity + 1 > item.quantity:
                    messages.error(request, f"Cannot add more {item.name}. Only {item.quantity} units left.")
                    return redirect('pharmacy-cart')
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity in cart was updated.")
            else:
                order.orderitems.add(order_item)
                messages.success(request, f"{item.name} was added to your cart.")
        else:
            order = Order.objects.create(user=request.user)
            order.orderitems.add(order_item)
            messages.success(request, f"{item.name} was added to your cart.")

        # Return to shop instead of cart to allow continuous shopping
        return redirect('pharmacy-shop')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def remove_from_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.name} was removed from your cart.")
            else:
                messages.info(request, "This item was not in your cart.")
        else:
            messages.info(request, "You don't have an active order.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def increase_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                # Check if increasing would exceed unit quantity
                if order_item.quantity + 1 > item.quantity:
                    messages.error(request, f"Cannot add more {item.name}. Only {item.quantity} units left.")
                    return redirect('pharmacy-cart')
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity in cart has been updated.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def decrease_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.info(request, f"{item.name} quantity in cart has been updated")
                else:
                    order.orderitems.remove(order_item)
                    order_item.delete()
                    messages.warning(request, f"{item.name} has been removed from your cart.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def checkout_view(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        orders = Order.objects.filter(user=request.user, ordered=False)

        if not carts.exists() or not orders.exists():
            messages.info(request, "Your cart is empty.")
            return redirect('pharmacy-shop')

        order = orders[0]
        
        if request.method == 'POST':
            delivery_method = request.POST.get('delivery_method', 'pickup')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_phone = request.POST.get('delivery_phone', patient.phone_number)
            
            # Update order with delivery information
            order.delivery_method = delivery_method
            if delivery_method == 'delivery':
                order.delivery_address = delivery_address
                order.delivery_phone = delivery_phone
            else:
                # For pickup, use patient's existing info
                order.delivery_phone = patient.phone_number
            order.save()
            
            # Redirect directly to Razorpay payment like other places
            return redirect('razorpay-pharmacy-payment', order_id=order.id)
        
        context = {
            'carts': carts,
            'order': order,
            'patient': patient
        }
        return render(request, 'Pharmacy/checkout_fixed.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def my_orders(request):
    """View for patients to see their medicine orders"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        
        # Get all completed orders for this patient (including COD orders)
        orders = Order.objects.filter(
            user=request.user, 
            ordered=True
        ).filter(
            Q(payment_status='paid') | Q(payment_status='cod') | Q(payment_status='cash_on_delivery')
        ).order_by('-created')
        
        context = {
            'orders': orders,
            'patient': patient
        }
        return render(request, 'Pharmacy/my_orders.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def upload_prescription(request):
    """View for patients to upload prescription images"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)

        if request.method == 'POST':
            prescription_image = request.FILES.get('prescription_image')
            doctor_name = request.POST.get('doctor_name', '')
            prescription_date = request.POST.get('prescription_date')
            patient_notes = request.POST.get('patient_notes', '')
            delivery_method = request.POST.get('delivery_method', 'pickup')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_phone = request.POST.get('delivery_phone', '')

            if prescription_image:
                prescription_upload = PrescriptionUpload.objects.create(
                    patient=patient,
                    prescription_image=prescription_image,
                    doctor_name=doctor_name,
                    prescription_date=prescription_date if prescription_date else None,
                    patient_notes=patient_notes,
                    delivery_method=delivery_method,
                    delivery_address=delivery_address,
                    delivery_phone=delivery_phone
                )

                messages.success(request, 'Prescription uploaded successfully! Our pharmacist will review it shortly.')
                return redirect('prescription_status', upload_id=prescription_upload.upload_id)
            else:
                messages.error(request, 'Please select a prescription image to upload.')

        context = {'patient': patient}
        return render(request, 'Pharmacy/upload_prescription.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def prescription_status(request, upload_id):
    """View for patients to check their prescription upload status"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription = get_object_or_404(PrescriptionUpload, upload_id=upload_id, patient=patient)

        context = {
            'patient': patient,
            'prescription': prescription
        }
        return render(request, 'Pharmacy/prescription_status.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def my_prescriptions(request):
    """View for patients to see all their prescription uploads"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescriptions = PrescriptionUpload.objects.filter(patient=patient).order_by('-uploaded_at')

        # Pagination
        paginator = Paginator(prescriptions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'patient': patient,
            'prescriptions': page_obj
        }
        return render(request, 'Pharmacy/my_prescriptions.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def pharmacist_prescriptions(request):
    """View for pharmacists to manage prescription uploads"""
    if request.user.is_authenticated and hasattr(request.user, 'pharmacist'):
        pharmacist = request.user.pharmacist

        # Filter prescriptions
        status_filter = request.GET.get('status', 'pending')
        prescriptions = PrescriptionUpload.objects.filter(status=status_filter).order_by('-uploaded_at')

        # Pagination
        paginator = Paginator(prescriptions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'pharmacist': pharmacist,
            'prescriptions': page_obj,
            'current_status': status_filter
        }
        return render(request, 'Pharmacy/pharmacist_prescriptions.html', context)
    else:
        messages.error(request, 'Not Authorized - Pharmacist access required')
        return redirect('login')


@csrf_exempt
@login_required(login_url="login")
def review_prescription(request, upload_id):
    """View for pharmacists to review and process prescription uploads"""
    if request.user.is_authenticated and hasattr(request.user, 'pharmacist'):
        pharmacist = request.user.pharmacist
        prescription = get_object_or_404(PrescriptionUpload, upload_id=upload_id)

        if request.method == 'POST':
            action = request.POST.get('action')
            pharmacist_notes = request.POST.get('pharmacist_notes', '')

            if action == 'approve':
                prescription.status = 'approved'
                prescription.pharmacist = pharmacist
                prescription.pharmacist_notes = pharmacist_notes
                prescription.reviewed_at = timezone.now()

                # Calculate estimated cost from added medicines
                total_cost = sum(med.total_price or 0 for med in prescription.medicines.all())
                prescription.estimated_cost = total_cost

                prescription.save()
                messages.success(request, f'Prescription #{upload_id} approved successfully!')

                # Send notification to patient (you can implement email notification here)
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings

                    if prescription.patient.email:
                        send_mail(
                            'Prescription Approved - Mahima Medicare',
                            f'Your prescription #{upload_id} has been approved by our pharmacist. Total cost: ₹{total_cost}. You can now proceed with payment.',
                            settings.DEFAULT_FROM_EMAIL,
                            [prescription.patient.email],
                            fail_silently=True
                        )
                except Exception as e:
                    messages.warning(request, f'Prescription approved but email notification failed: {e}')

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
                            f'Your prescription #{upload_id} has been reviewed. Please check the pharmacist notes in your account.',
                            settings.DEFAULT_FROM_EMAIL,
                            [prescription.patient.email],
                            fail_silently=True
                        )
                except Exception:
                    pass

            return redirect('pharmacist_prescriptions')

        # Handle medicine addition via AJAX
        if request.GET.get('add_medicine'):
            medicine_id = request.GET.get('medicine_id')
            quantity = int(request.GET.get('quantity', 1))
            dosage = request.GET.get('dosage', '')
            days = request.GET.get('days')

            medicine = get_object_or_404(Medicine, serial_number=medicine_id)

            prescription_med, created = PrescriptionMedicine.objects.get_or_create(
                prescription_upload=prescription,
                medicine=medicine,
                defaults={
                    'quantity': quantity,
                    'dosage': dosage,
                    'days': int(days) if days else None,
                    'unit_price': medicine.price
                }
            )

            if not created:
                prescription_med.quantity = quantity
                prescription_med.dosage = dosage
                prescription_med.days = int(days) if days else None
                prescription_med.save()

            messages.success(request, f'Added {medicine.name} to prescription')
            return redirect('review_prescription', upload_id=upload_id)

        # Get available medicines for adding to prescription
        medicines = Medicine.objects.filter(quantity__gt=0).order_by('name')

        context = {
            'pharmacist': pharmacist,
            'prescription': prescription,
            'medicines': medicines
        }
        return render(request, 'Pharmacy/review_prescription.html', context)
    else:
        messages.error(request, 'Not Authorized - Pharmacist access required')
        return redirect('login')


@csrf_exempt
@login_required(login_url="login")
def doctor_prescriptions(request):
    """View for patients to see their doctor's digital prescriptions"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)

        # Get all prescriptions for this patient from doctor module
        from doctor.models import Prescription, Prescription_medicine
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescription_id')

        # Add medicine details for each prescription
        for prescription in prescriptions:
            prescription.medicines = Prescription_medicine.objects.filter(prescription=prescription)

        context = {
            'patient': patient,
            'prescriptions': prescriptions
        }
        return render(request, 'Pharmacy/doctor_prescriptions.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def prescription_to_pharmacy(request, prescription_id):
    """Convert doctor's prescription to pharmacy order"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)

        from doctor.models import Prescription, Prescription_medicine
        prescription = get_object_or_404(Prescription, prescription_id=prescription_id, patient=patient)

        if request.method == 'POST':
            delivery_method = request.POST.get('delivery_method', 'pickup')
            delivery_address = request.POST.get('delivery_address', '')
            delivery_phone = request.POST.get('delivery_phone', '')

            # Create prescription upload linked to doctor's prescription
            prescription_upload = PrescriptionUpload.objects.create(
                patient=patient,
                doctor_prescription=prescription,
                doctor_name=prescription.doctor.name if prescription.doctor else 'Unknown Doctor',
                prescription_date=prescription.create_date,
                status='auto_approved',  # Auto-approve since it's from doctor
                delivery_method=delivery_method,
                delivery_address=delivery_address,
                delivery_phone=delivery_phone
            )

            # Get prescription medicines and try to match with pharmacy medicines
            prescription_medicines = Prescription_medicine.objects.filter(prescription=prescription)
            total_cost = 0
            matched_medicines = []
            unmatched_medicines = []

            for presc_med in prescription_medicines:
                # Try to find matching medicine in pharmacy
                medicine_matches = Medicine.objects.filter(
                    name__icontains=presc_med.medicine_name
                ).order_by('name')

                if medicine_matches.exists():
                    medicine = medicine_matches.first()
                    quantity = int(presc_med.quantity) if presc_med.quantity and presc_med.quantity.isdigit() else 1

                    # Create prescription medicine record
                    PrescriptionMedicine.objects.create(
                        prescription_upload=prescription_upload,
                        medicine=medicine,
                        quantity=quantity,
                        dosage=f"{presc_med.frequency} - {presc_med.relation_with_meal}",
                        days=int(presc_med.duration) if presc_med.duration and presc_med.duration.isdigit() else None,
                        unit_price=medicine.price,
                        total_price=medicine.price * quantity
                    )

                    total_cost += float(medicine.price * quantity)
                    matched_medicines.append({
                        'name': presc_med.medicine_name,
                        'pharmacy_medicine': medicine,
                        'quantity': quantity,
                        'price': medicine.price * quantity
                    })
                else:
                    unmatched_medicines.append(presc_med.medicine_name)

            # Add delivery charges if applicable
            if delivery_method == 'delivery':
                total_cost += 40

            # Update estimated cost
            prescription_upload.estimated_cost = total_cost
            prescription_upload.save()

            # If all medicines matched, auto-approve and create order
            if not unmatched_medicines:
                prescription_upload.status = 'approved'
                prescription_upload.save()

                messages.success(request, f'Prescription converted to pharmacy order successfully! Total: ₹{total_cost:.2f}')
                return redirect('prescription_status', upload_id=prescription_upload.upload_id)
            else:
                prescription_upload.status = 'pending'
                prescription_upload.pharmacist_notes = f"Unmatched medicines: {', '.join(unmatched_medicines)}"
                prescription_upload.save()

                messages.warning(request, f'Some medicines need pharmacist review. Matched: {len(matched_medicines)}, Unmatched: {len(unmatched_medicines)}')
                return redirect('prescription_status', upload_id=prescription_upload.upload_id)

        # GET request - show prescription details and conversion form
        prescription_medicines = Prescription_medicine.objects.filter(prescription=prescription)

        context = {
            'patient': patient,
            'prescription': prescription,
            'prescription_medicines': prescription_medicines
        }
        return render(request, 'Pharmacy/prescription_to_pharmacy.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def prescription_to_cart(request, prescription_upload_id):
    """Add approved prescription medicines to cart"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription_upload = get_object_or_404(PrescriptionUpload, upload_id=prescription_upload_id, patient=patient)
        
        if prescription_upload.status != 'approved':
            messages.error(request, 'Prescription is not approved yet.')
            return redirect('prescription_status', upload_id=prescription_upload_id)
        
        # Get or create cart order for this user
        order, created = Order.objects.get_or_create(
            user=request.user,
            ordered=False,
            defaults={
                'delivery_method': prescription_upload.delivery_method,
                'delivery_address': prescription_upload.delivery_address,
                'delivery_phone': prescription_upload.delivery_phone
            }
        )
        
        added_count = 0
        for prescription_medicine in prescription_upload.medicines.all():
            # Check if medicine is already in cart
            existing_cart_item = Cart.objects.filter(
                user=request.user,
                item=prescription_medicine.medicine,
                purchased=False
            ).first()
            
            if existing_cart_item:
                existing_cart_item.quantity += prescription_medicine.quantity
                existing_cart_item.save()
            else:
                cart_item = Cart.objects.create(
                    user=request.user,
                    item=prescription_medicine.medicine,
                    quantity=prescription_medicine.quantity,
                    purchased=False
                )
                order.orderitems.add(cart_item)
            
            added_count += 1
        
        messages.success(request, f'Successfully added {added_count} medicines to your cart!')
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def prescription_payment_redirect(request, prescription_upload_id):
    """Redirect to Razorpay prescription payment"""
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription_upload = get_object_or_404(PrescriptionUpload, upload_id=prescription_upload_id, patient=patient)
        
        if prescription_upload.status != 'approved':
            messages.error(request, 'Prescription is not approved yet.')
            return redirect('prescription_status', upload_id=prescription_upload_id)
        
        # Redirect to Razorpay prescription payment
        return redirect('razorpay-prescription-payment', prescription_upload_id=prescription_upload_id)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
def ajax_medicine_search(request):
    """AJAX endpoint for live medicine search"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        if len(query) < 1:
            return JsonResponse({'medicines': []})
        
        # Search medicines by name, description, category, or type
        from django.db.models import Q
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(medicine_category__icontains=query) |
            Q(medicine_type__icontains=query),
            quantity__gt=0  # Only show in-stock medicines
        ).order_by('name')[:10]  # Limit to 10 results for performance
        
        # Serialize medicine data
        medicine_data = []
        for med in medicines:
            medicine_data.append({
                'id': med.serial_number,
                'name': med.name,
                'price': float(med.price) if med.price else 0.0,
                'description': med.description or '',
                'category': med.medicine_category or '',
                'type': med.medicine_type or '',
                'stock': med.quantity,
                'image_url': med.get_medicine_image()
            })
        
        return JsonResponse({'medicines': medicine_data})
