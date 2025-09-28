from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import razorpay
import json
import hmac
import hashlib
from decimal import Decimal

from .models import RazorpayPayment, Invoice
from .invoice_utils import generate_invoice_for_payment, InvoicePDFGenerator
from doctor.models import Appointment, testOrder, Prescription
from hospital.models import Patient
from pharmacy.models import Order

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def generate_receipt_id(payment_type, item_id):
    """Generate unique receipt ID"""
    import random
    import string
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{payment_type}_{item_id}_{random_string}"

@login_required
def create_appointment_payment(request, appointment_id):
    """Create Razorpay order for appointment payment"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        patient = appointment.patient
        
        # Calculate amount (convert to paise for Razorpay)
        if appointment.appointment_type == 'checkup':
            fee = appointment.doctor.consultation_fee or 0
            amount = int(float(fee) * 100)
        else:
            fee = appointment.doctor.report_fee or 0
            amount = int(float(fee) * 100)
        
        # Create Razorpay order
        receipt_id = generate_receipt_id('appointment', appointment_id)
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt_id,
            'notes': {
                'appointment_id': appointment_id,
                'patient_id': patient.patient_id,
                'doctor_name': appointment.doctor.name,
                'appointment_type': appointment.appointment_type
            }
        })
        
        # Save payment record
        payment = RazorpayPayment.objects.create(
            razorpay_order_id=razorpay_order['id'],
            patient=patient,
            appointment=appointment,
            payment_type='appointment',
            amount=Decimal(amount) / 100,
            name=patient.name,
            email=patient.email,
            phone=patient.phone_number,
            address=patient.address,
            receipt=receipt_id,
            notes=razorpay_order['notes']
        )
        
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Mahima Medicare',
            'description': f'Appointment with Dr. {appointment.doctor.name}',
            'customer_name': patient.name,
            'customer_email': patient.email,
            'customer_phone': patient.phone_number,
            'appointment': appointment,
            'payment': payment
        }
        
        return render(request, 'razorpay_payment/appointment_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}')
        return redirect('patient-dashboard')

@login_required
def create_pharmacy_payment(request, order_id):
    """Create Razorpay order for pharmacy payment with COD option"""
    try:
        order = get_object_or_404(Order, id=order_id)
        patient = order.user.patient
        
        # Calculate amount (convert to paise for Razorpay)
        amount_in_rupees = float(order.final_bill())
        
        # Check if payment method is provided
        payment_method = request.GET.get('method', 'online')
        
        # Handle Cash on Delivery (COD) for pharmacy
        if payment_method == 'cod':
            # Mark as COD and proceed without Razorpay
            order.payment_status = 'cod'
            order.ordered = True
            order.order_status = 'confirmed_cod'
            order.save()
            
            # Mark cart items as purchased
            for cart_item in order.orderitems.all():
                cart_item.purchased = True
                cart_item.save()
            
            messages.success(request, 'Order confirmed with Cash on Delivery. Please pay upon receiving your medicines.')
            return redirect('patient-dashboard')
            
        amount = int(amount_in_rupees * 100)
        
        # Create Razorpay order with retry mechanism
        receipt_id = generate_receipt_id('pharmacy', order_id)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                razorpay_order = razorpay_client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'receipt': receipt_id,
                    'notes': {
                        'order_id': order_id,
                        'patient_id': patient.patient_id,
                        'total_items': order.orderitems.count()
                    }
                })
                break  # Success, exit retry loop
            except Exception as conn_error:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    # All retries failed, offer COD as fallback
                    messages.error(request, f'Payment gateway temporarily unavailable. Would you like to proceed with Cash on Delivery?')
                    context = {
                        'order': order,
                        'amount': amount_in_rupees,
                        'payment_error': True,
                        'error_message': 'Payment gateway connection failed. Please try again or choose Cash on Delivery.',
                        'show_cod_option': True
                    }
                    return render(request, 'razorpay_payment/pharmacy_payment.html', context)
        
        # Save payment record
        payment = RazorpayPayment.objects.create(
            razorpay_order_id=razorpay_order['id'],
            patient=patient,
            order=order,
            payment_type='pharmacy',
            amount=Decimal(amount) / 100,
            name=patient.name,
            email=patient.email,
            phone=patient.phone_number,
            address=patient.address,
            receipt=receipt_id,
            notes=razorpay_order['notes']
        )
        
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Mahima Medicare',
            'description': f'Pharmacy Order #{order_id}',
            'customer_name': patient.name,
            'customer_email': patient.email,
            'customer_phone': patient.phone_number,
            'order': order,
            'payment': payment,
            'show_cod_option': True  # Always show COD option for pharmacy
        }
        
        return render(request, 'razorpay_payment/pharmacy_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}. You can still proceed with Cash on Delivery.')
        return redirect(f'/razorpay/pharmacy/{order_id}/?method=cod_fallback')

@login_required
def create_test_payment(request, test_order_id):
    """Create Razorpay order for test payment with COD option"""
    try:
        test_order = get_object_or_404(testOrder, id=test_order_id)
        # Get patient from the user associated with the test order
        try:
            patient = test_order.user.patient
        except AttributeError:
            # If user doesn't have patient profile, get from current user
            patient = request.user.patient
        
        # Calculate amount (convert to paise for Razorpay)
        if hasattr(test_order, 'final_bill'):
            total_bill = test_order.final_bill
        elif hasattr(test_order, 'total_amount'):
            total_bill = test_order.total_amount
        else:
            total_bill = 0
            
        if total_bill <= 0:
            messages.error(request, 'Invalid test order amount.')
            return redirect('patient-dashboard')
            
        # Check if payment method is provided
        payment_method = request.GET.get('method', 'online')
        
        # Handle Cash on Delivery (COD) for tests
        if payment_method == 'cod':
            # Mark as unpaid/COD and proceed without Razorpay
            test_order.payment_status = 'cod_pending'
            test_order.ordered = True
            test_order.save()
            
            # Update cart items
            for cart_item in test_order.orderitems.all():
                cart_item.purchased = True
                if hasattr(cart_item, 'item') and cart_item.item:
                    prescription_test = cart_item.item
                    prescription_test.test_info_pay_status = 'cod_pending'
                    prescription_test.save()
                cart_item.save()
            
            messages.success(request, 'Test order confirmed with Cash on Delivery. Please pay at the lab.')
            return redirect('patient-dashboard')
            
        amount = int(float(total_bill) * 100)
        
        # Create Razorpay order with retry mechanism for connection errors
        receipt_id = generate_receipt_id('test', test_order_id)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                razorpay_order = razorpay_client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'receipt': receipt_id,
                    'notes': {
                        'test_order_id': test_order_id,
                        'patient_id': patient.patient_id,
                        'prescription_id': getattr(test_order.prescription, 'prescription_id', None) if hasattr(test_order, 'prescription') and test_order.prescription else None
                    }
                })
                break  # Success, exit retry loop
            except Exception as conn_error:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    # All retries failed, offer COD as fallback
                    messages.error(request, f'Payment gateway temporarily unavailable. Would you like to proceed with Cash on Delivery?')
                    context = {
                        'test_order': test_order,
                        'amount': total_bill,
                        'payment_error': True,
                        'error_message': 'Payment gateway connection failed. Please try again or choose Cash on Delivery.'
                    }
                    return render(request, 'razorpay_payment/test_payment.html', context)
        
        # Save payment record
        payment = RazorpayPayment.objects.create(
            razorpay_order_id=razorpay_order['id'],
            patient=patient,
            test_order=test_order,
            prescription=getattr(test_order, 'prescription', None),
            payment_type='test',
            amount=Decimal(amount) / 100,
            name=patient.name,
            email=patient.email,
            phone=patient.phone_number,
            address=patient.address,
            receipt=receipt_id,
            notes=razorpay_order['notes']
        )
        
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Mahima Medicare',
            'description': f'Lab Test Order #{test_order_id}',
            'customer_name': patient.name,
            'customer_email': patient.email,
            'customer_phone': patient.phone_number,
            'test_order': test_order,
            'payment': payment,
            'show_cod_option': True  # Always show COD option for tests
        }
        
        return render(request, 'razorpay_payment/test_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}. You can still proceed with Cash on Delivery.')
        # Redirect with COD option
        return redirect(f'/razorpay/test/{test_order_id}/?method=cod_fallback')

@csrf_exempt
def payment_success(request):
    """Handle successful payment"""
    if request.method == 'POST':
        try:
            # Get payment details from request
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Get payment record
            payment = get_object_or_404(RazorpayPayment, razorpay_order_id=razorpay_order_id)
            
            # Update payment record
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'captured'
            payment.save()
            
            # Update related models based on payment type
            if payment.payment_type == 'appointment' and payment.appointment:
                payment.appointment.payment_status = 'paid'
                payment.appointment.save()
                
            elif payment.payment_type == 'pharmacy' and payment.order:
                # Update payment status
                payment.order.payment_status = 'paid'
                payment.order.ordered = True
                payment.order.order_status = 'confirmed'  # Set initial status after payment
                payment.order.save()
                
                # Update stock quantities
                try:
                    payment.order.stock_quantity_decrease()
                except ValueError as e:
                    messages.warning(request, f'Stock update warning: {str(e)}')
                
                # Mark cart items as purchased
                for cart_item in payment.order.orderitems.all():
                    cart_item.purchased = True
                    cart_item.save()
                
            elif payment.payment_type == 'test' and payment.test_order:
                payment.test_order.payment_status = 'paid'
                payment.test_order.save()
                
                # Update individual Prescription_test payment status
                from doctor.models import Prescription_test
                from django.utils import timezone
                
                # Get all test cart items in this order and update their prescription tests
                try:
                    print(f"DEBUG: Processing test order: {payment.test_order}")
                    cart_items = payment.test_order.orderitems.all()
                    print(f"DEBUG: Found {cart_items.count()} cart items")
                    
                    if cart_items.count() == 0:
                        print("DEBUG: No cart items found - checking alternative approach")
                        # Alternative: try to find cart items directly
                        from doctor.models import testCart
                        alt_cart_items = testCart.objects.filter(user=payment.user, purchased=False)
                        print(f"DEBUG: Found {alt_cart_items.count()} unpurchased cart items for user")
                        
                        # Use alternative cart items if main relationship is empty
                        if alt_cart_items.exists():
                            cart_items = alt_cart_items
                            print("DEBUG: Using alternative cart items")
                    
                    for cart_item in cart_items:
                        print(f"Processing cart item: {cart_item}")
                        if hasattr(cart_item, 'item') and cart_item.item:
                            prescription_test = cart_item.item
                            print(f"Updating prescription test: {prescription_test}")
                            
                            # Update payment status (this field should exist)
                            prescription_test.test_info_pay_status = 'paid'
                            
                            # Only update new fields if they exist
                            if hasattr(prescription_test, 'payment_date'):
                                prescription_test.payment_date = timezone.now()
                            
                            if hasattr(prescription_test, 'test_status'):
                                if prescription_test.test_status == 'prescribed':
                                    prescription_test.test_status = 'paid'
                            
                            prescription_test.save()
                            print(f"Updated prescription test payment status to: {prescription_test.test_info_pay_status}")
                            
                            # Mark cart item as purchased
                            cart_item.purchased = True
                            cart_item.save()
                            print(f"Marked cart item as purchased: {cart_item.purchased}")
                except Exception as e:
                    # Log the error but don't fail the payment
                    print(f"Error updating prescription test status: {e}")
                    # Still mark cart items as purchased for backward compatibility
                    try:
                        for cart_item in payment.test_order.orderitems.all():
                            cart_item.purchased = True
                            cart_item.save()
                    except Exception as e2:
                        print(f"Error in fallback cart update: {e2}")
            
            # Generate invoice automatically after successful payment
            try:
                invoice = generate_invoice_for_payment(payment)
                messages.success(request, 'Payment successful! Invoice generated.')
                return render(request, 'razorpay_payment/payment_success.html', {
                    'payment': payment,
                    'invoice': invoice
                })
            except Exception as e:
                messages.success(request, 'Payment successful!')
                messages.warning(request, f'Invoice generation failed: {str(e)}')
                return render(request, 'razorpay_payment/payment_success.html', {'payment': payment})
            
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment verification failed!')
            return render(request, 'razorpay_payment/payment_failed.html')
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            return render(request, 'razorpay_payment/payment_failed.html')
    
    return redirect('patient-dashboard')

@csrf_exempt
def payment_failed(request):
    """Handle failed payment"""
    razorpay_order_id = request.POST.get('razorpay_order_id')
    
    if razorpay_order_id:
        try:
            payment = RazorpayPayment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.status = 'failed'
            payment.save()
        except RazorpayPayment.DoesNotExist:
            pass
    
    messages.error(request, 'Payment failed. Please try again.')
    return render(request, 'razorpay_payment/payment_failed.html')

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhooks"""
    if request.method == 'POST':
        try:
            # Verify webhook signature (if webhook secret is configured)
            webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
            webhook_body = request.body
            
            # Process webhook data
            webhook_data = json.loads(webhook_body)
            event = webhook_data.get('event')
            
            if event == 'payment.captured':
                payment_entity = webhook_data['payload']['payment']['entity']
                order_id = payment_entity['order_id']
                
                try:
                    payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)
                    payment.status = 'captured'
                    payment.razorpay_payment_id = payment_entity['id']
                    payment.save()
                except RazorpayPayment.DoesNotExist:
                    pass
            
            elif event == 'payment.failed':
                payment_entity = webhook_data['payload']['payment']['entity']
                order_id = payment_entity['order_id']
                
                try:
                    payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)
                    payment.status = 'failed'
                    payment.save()
                except RazorpayPayment.DoesNotExist:
                    pass
            
            return HttpResponse(status=200)
            
        except Exception as e:
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)


@login_required
def download_invoice(request, invoice_id):
    """Download invoice PDF"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        # Check if user has permission to download this invoice
        if hasattr(request.user, 'patient'):
            patient = request.user.patient
            if invoice.payment.patient != patient:
                messages.error(request, 'You do not have permission to access this invoice.')
                return redirect('patient-dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('patient-dashboard')
        
        # Check if PDF exists
        if not invoice.pdf_file:
            # Generate PDF if it doesn't exist
            pdf_generator = InvoicePDFGenerator(invoice)
            pdf_content = pdf_generator.generate_pdf()
            
            # Save PDF to invoice
            from django.core.files.base import ContentFile
            pdf_file = ContentFile(pdf_content)
            invoice.pdf_file.save(
                f"invoice_{invoice.invoice_number}.pdf",
                pdf_file,
                save=True
            )
        
        # Serve the PDF file
        from django.http import FileResponse
        response = FileResponse(
            invoice.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"Invoice_{invoice.invoice_number}.pdf"
        )
        response['Content-Type'] = 'application/pdf'
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def view_invoice(request, invoice_id):
    """View invoice details"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        # Check if user has permission to view this invoice
        if hasattr(request.user, 'patient'):
            patient = request.user.patient
            if invoice.payment.patient != patient:
                messages.error(request, 'You do not have permission to access this invoice.')
                return redirect('patient-dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('patient-dashboard')
        
        context = {
            'invoice': invoice,
            'payment': invoice.payment
        }
        
        return render(request, 'razorpay_payment/invoice_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Error viewing invoice: {str(e)}')
        return redirect('patient-dashboard')


@login_required(login_url='login')
def regenerate_invoice(request, payment_id):
    """Regenerate invoice for a payment"""
    try:
        payment = get_object_or_404(RazorpayPayment, id=payment_id)
        
        # Check permissions
        if hasattr(request.user, 'patient') and request.user.patient != payment.patient:
            messages.error(request, 'You do not have permission to access this invoice.')
            return redirect('patient-dashboard')
        
        # Generate new invoice
        invoice = generate_invoice_for_payment(payment)
        
        if invoice:
            messages.success(request, 'Invoice regenerated successfully!')
        else:
            messages.error(request, 'Failed to regenerate invoice.')
            
    except Exception as e:
        messages.error(request, f'Error regenerating invoice: {str(e)}')
    
    return redirect('patient-dashboard')


@csrf_exempt
@login_required(login_url='login')
def download_pharmacy_invoice(request, order_id):
    """Download pharmacy invoice PDF"""
    try:
        from pharmacy.models import Order
        order = get_object_or_404(Order, id=order_id)
        
        # Check permissions - only the patient who made the order can download
        if request.user != order.user:
            messages.error(request, 'You do not have permission to access this invoice.')
            return redirect('patient-dashboard')
        
        # Generate invoice PDF
        from .invoice_utils import generate_pharmacy_invoice_pdf
        pdf_content = generate_pharmacy_invoice_pdf(order)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="pharmacy_invoice_{order.id}.pdf"'
            return response
        else:
            messages.error(request, 'Failed to generate invoice PDF.')
            return redirect('patient-dashboard')
            
    except Exception as e:
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('patient-dashboard')


# COD (Cash on Delivery) Views
@login_required
def cod_test_payment(request, test_order_id):
    """Handle Cash on Delivery for test orders"""
    try:
        test_order = get_object_or_404(testOrder, id=test_order_id)
        
        # Check if user has permission
        if test_order.user != request.user:
            messages.error(request, 'You do not have permission to access this order.')
            return redirect('patient-dashboard')
        
        # Mark as COD and proceed
        test_order.payment_status = 'cash_on_delivery'
        test_order.ordered = True
        test_order.save()
        
        # Update cart items
        for cart_item in test_order.orderitems.all():
            cart_item.purchased = True
            if hasattr(cart_item, 'item') and cart_item.item:
                prescription_test = cart_item.item
                prescription_test.test_info_pay_status = 'cash_on_delivery'
                prescription_test.save()
            cart_item.save()
        
        # Send notification email to admin
        send_cod_notification_email('test', test_order)
        
        messages.success(request, 'Test order confirmed with Cash on Delivery. Please pay at the lab.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        messages.error(request, f'Error processing COD order: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def cod_pharmacy_payment(request, order_id):
    """Handle Cash on Delivery for pharmacy orders"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user has permission
        if order.user != request.user:
            messages.error(request, 'You do not have permission to access this order.')
            return redirect('patient-dashboard')
        
        # Mark as COD and proceed
        order.payment_status = 'cash_on_delivery'
        order.ordered = True
        order.order_status = 'confirmed'
        order.save()
        
        # Mark cart items as purchased
        for cart_item in order.orderitems.all():
            cart_item.purchased = True
            cart_item.save()
        
        # Send notification email to admin
        send_cod_notification_email('pharmacy', order)
        
        messages.success(request, 'Order confirmed with Cash on Delivery. Please pay upon receiving your medicines.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        messages.error(request, f'Error processing COD order: {str(e)}')
        return redirect('patient-dashboard')


# Standalone Test Booking for Patients
def standalone_test_booking(request):
    """Allow patients to book lab tests independently"""
    try:
        # Get all available tests from Test_Information model (managed by lab technicians)
        from hospital_admin.models import Test_Information
        available_tests = Test_Information.objects.all().order_by('test_name')
        
        # Convert to list of dictionaries for template compatibility
        test_list = []
        for test in available_tests:
            test_list.append({
                'id': test.test_id,
                'name': test.test_name,
                'price': int(test.test_price) if test.test_price and test.test_price.isdigit() else 0,
                'description': f'Lab test: {test.test_name}'
            })
        
        context = {
            'available_tests': test_list,
        }
        
        return render(request, 'razorpay_payment/standalone_test_booking.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading test booking page: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def submit_standalone_test(request):
    """Submit standalone test booking"""
    if request.method == 'POST':
        try:
            selected_tests = request.POST.getlist('selected_tests')
            payment_method = request.POST.get('payment_method', 'online')
            
            if not selected_tests:
                messages.error(request, 'Please select at least one test.')
                return redirect('standalone-test-booking')
            
            # Get patient
            patient = request.user.patient
            
            # Create test cart items
            from doctor.models import testCart, Prescription_test, testOrder
            from hospital_admin.models import Test_Information
            
            # Create a dummy prescription for standalone tests
            prescription = None
            
            cart_items = []
            total_amount = 0
            
            for test_id in selected_tests:
                test_id = int(test_id)
                try:
                    # Get the actual test from Test_Information model
                    lab_test = Test_Information.objects.get(test_id=test_id)
                    
                    # Create prescription test entry
                    prescription_test = Prescription_test.objects.create(
                        test_name=lab_test.test_name,
                        test_description=f'Standalone booking: {lab_test.test_name}',
                        test_info_price=lab_test.test_price or '0',
                        test_info_pay_status='unpaid',
                        test_status='prescribed'
                    )
                    
                    # Create cart item
                    cart_item = testCart.objects.create(
                        user=request.user,
                        item=prescription_test,
                        purchased=False
                    )
                    cart_items.append(cart_item)
                    test_price = int(lab_test.test_price) if lab_test.test_price and lab_test.test_price.isdigit() else 0
                    total_amount += test_price
                    
                except Test_Information.DoesNotExist:
                    messages.error(request, f'Test with ID {test_id} not found.')
                    continue
            
            # Create test order
            test_order = testOrder.objects.create(
                user=request.user,
                ordered=False,
                payment_status='pending'
            )
            test_order.orderitems.set(cart_items)
            
            # Handle payment method
            if payment_method == 'cod':
                # Direct COD processing
                test_order.payment_status = 'cod_pending'
                test_order.ordered = True
                test_order.save()
                
                # Update cart items
                for cart_item in cart_items:
                    cart_item.purchased = True
                    cart_item.item.test_info_pay_status = 'cod_pending'
                    cart_item.item.save()
                    cart_item.save()
                
                # Send notification
                send_cod_notification_email('standalone_test', test_order)
                
                messages.success(request, 'Lab tests booked successfully with Cash on Delivery. Please pay at the lab.')
                return redirect('patient-dashboard')
            else:
                # Redirect to payment
                return redirect('razorpay-test-payment', test_order_id=test_order.id)
            
        except Exception as e:
            messages.error(request, f'Error booking tests: {str(e)}')
            return redirect('standalone-test-booking')
    
    return redirect('standalone-test-booking')


def send_cod_notification_email(order_type, order):
    """Send COD notification email to admin"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Admin email (you can add this to your .env file)
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@mahimamedicare.com')
        
        if order_type == 'test':
            subject = f'New COD Test Order #{order.id}'
            message = f"""
            New Cash on Delivery test order received:
            
            Order ID: {order.id}
            Patient: {order.user.patient.name if hasattr(order.user, 'patient') else order.user.username}
            Phone: {order.user.patient.phone_number if hasattr(order.user, 'patient') else 'N/A'}
            Total Amount: ₹{order.final_bill if hasattr(order, 'final_bill') else order.total_amount}
            Order Date: {order.created}
            
            Please ensure payment collection at the lab.
            """
        elif order_type == 'pharmacy':
            subject = f'New COD Pharmacy Order #{order.id}'
            message = f"""
            New Cash on Delivery pharmacy order received:
            
            Order ID: {order.id}
            Patient: {order.user.patient.name if hasattr(order.user, 'patient') else order.user.username}
            Phone: {order.user.patient.phone_number if hasattr(order.user, 'patient') else 'N/A'}
            Total Amount: ₹{order.final_bill()}
            Order Date: {order.created_at if hasattr(order, 'created_at') else 'N/A'}
            
            Please ensure payment collection upon delivery.
            """
        elif order_type == 'standalone_test':
            subject = f'New Standalone Test Booking (COD) #{order.id}'
            message = f"""
            New standalone test booking with Cash on Delivery:
            
            Order ID: {order.id}
            Patient: {order.user.patient.name if hasattr(order.user, 'patient') else order.user.username}
            Phone: {order.user.patient.phone_number if hasattr(order.user, 'patient') else 'N/A'}
            Total Amount: ₹{order.final_bill if hasattr(order, 'final_bill') else order.total_amount}
            Order Date: {order.created}
            
            This is a self-booked test by the patient.
            Please ensure payment collection at the lab.
            """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=True
        )
        
    except Exception as e:
        print(f"Error sending COD notification email: {e}")


@csrf_exempt
@login_required(login_url='login')
def view_pharmacy_invoice(request, order_id):
    """View pharmacy invoice in browser"""
    try:
        from pharmacy.models import Order
        order = get_object_or_404(Order, id=order_id)
        
        # Check permissions - only the patient who made the order can view
        if request.user != order.user:
            messages.error(request, 'You do not have permission to access this invoice.')
            return redirect('patient-dashboard')
        
        # Generate invoice PDF
        from .invoice_utils import generate_pharmacy_invoice_pdf
        pdf_content = generate_pharmacy_invoice_pdf(order)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="pharmacy_invoice_{order.id}.pdf"'
            return response
        else:
            messages.error(request, 'Failed to generate invoice PDF.')
            return redirect('patient-dashboard')
            
    except Exception as e:
        messages.error(request, f'Error viewing invoice: {str(e)}')
        return redirect('patient-dashboard')
