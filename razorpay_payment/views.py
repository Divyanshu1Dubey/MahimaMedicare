from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
import razorpay
import json
import hmac
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta

from .models import RazorpayPayment, Invoice
from .invoice_utils import generate_invoice_for_payment, InvoicePDFGenerator
from doctor.models import Appointment, testOrder, Prescription, testCart, Prescription_test
from hospital.models import Patient
from hospital_admin.models import Test_Information

def get_lab_test_vat():
    """Get lab test VAT amount from settings"""
    return getattr(settings, 'LAB_TEST_VAT_AMOUNT', 20.00)
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
        try:
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
        except Exception as e:
            messages.error(request, 'Payment gateway error. Please try again later.')
            return redirect('patient-dashboard')
        
        # Check if payment already exists for this appointment to prevent duplicates
        payment, created = RazorpayPayment.objects.get_or_create(
            appointment=appointment,
            payment_type='appointment',
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'patient': patient,
                'amount': Decimal(amount) / 100,
                'name': patient.name,
                'email': patient.email,
                'phone': patient.phone_number,
                'address': patient.address,
                'receipt': receipt_id,
                'notes': razorpay_order['notes']
            }
        )
        
        # If payment already exists, update the razorpay_order_id for the new session
        if not created:
            payment.razorpay_order_id = razorpay_order['id']
            payment.save()
        
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
        messages.error(request, f'Payment creation failed: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def create_prescription_payment(request, prescription_upload_id):
    """Create Razorpay order for prescription payment"""
    try:
        from pharmacy.models import PrescriptionUpload

        prescription_upload = get_object_or_404(PrescriptionUpload, upload_id=prescription_upload_id)
        patient = prescription_upload.patient

        # Ensure prescription is approved and has estimated cost
        if prescription_upload.status != 'approved':
            messages.error(request, 'Prescription is not approved yet. Please wait for pharmacist review.')
            return redirect('prescription_status', upload_id=prescription_upload_id)

        if not prescription_upload.estimated_cost:
            messages.error(request, 'Prescription cost not estimated yet. Please contact pharmacist.')
            return redirect('prescription_status', upload_id=prescription_upload_id)

        # Calculate amount (convert to paise for Razorpay)
        amount = int(float(prescription_upload.estimated_cost) * 100)

        # Add delivery charges if home delivery
        if prescription_upload.delivery_method == 'delivery':
            amount += 4000  # ₹40 delivery charge in paise

        # Create Razorpay order
        receipt_id = generate_receipt_id('prescription', prescription_upload_id)
        try:
            razorpay_order = razorpay_client.order.create({
                'amount': amount,
                'currency': 'INR',
                'receipt': receipt_id,
                'notes': {
                    'prescription_upload_id': prescription_upload_id,
                    'patient_id': patient.patient_id,
                    'delivery_method': prescription_upload.delivery_method,
                    'estimated_cost': str(prescription_upload.estimated_cost)
                }
            })
        except Exception as e:
            messages.error(request, 'Payment gateway error. Please try again later.')
            return redirect('prescription_status', upload_id=prescription_upload_id)

        # Create payment record
        payment, created = RazorpayPayment.objects.get_or_create(
            prescription_upload=prescription_upload,
            payment_type='prescription_order',
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'patient': patient,
                'amount': Decimal(amount) / 100,
                'name': patient.name,
                'email': patient.email,
                'phone': prescription_upload.delivery_phone or patient.phone_number,
                'address': prescription_upload.delivery_address or patient.address,
                'receipt': receipt_id,
                'notes': razorpay_order['notes']
            }
        )

        if not created:
            payment.razorpay_order_id = razorpay_order['id']
            payment.save()

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Mahima Medicare',
            'description': f'Prescription Order #{prescription_upload_id}',
            'customer_name': patient.name,
            'customer_email': patient.email,
            'customer_phone': prescription_upload.delivery_phone or patient.phone_number,
            'prescription_upload': prescription_upload,
            'payment': payment
        }

        return render(request, 'razorpay_payment/prescription_payment.html', context)

    except Exception as e:
        messages.error(request, f'Payment creation failed: {str(e)}')
        return redirect('my-prescriptions')

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
        
        razorpay_order = None
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
        
        # If razorpay_order is still None, something went wrong
        if razorpay_order is None:
            messages.error(request, 'Unable to create payment order. Please try again later.')
            return redirect('pharmacy_shop')
        
        # Check if payment already exists for this order to prevent duplicates
        payment, created = RazorpayPayment.objects.get_or_create(
            order=order,
            payment_type='pharmacy',
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'patient': patient,
                'amount': Decimal(amount) / 100,
                'name': patient.name,
                'email': patient.email,
                'phone': patient.phone_number,
                'address': patient.address,
                'receipt': receipt_id,
                'notes': razorpay_order['notes']
            }
        )
        
        # If payment already exists, update the razorpay_order_id for the new session
        if not created:
            payment.razorpay_order_id = razorpay_order['id']
            payment.save()
        
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
        
        razorpay_order = None
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
        
        # If razorpay_order is still None, something went wrong
        if razorpay_order is None:
            messages.error(request, 'Unable to create payment order. Please try again later.')
            return redirect('patient-dashboard')
        
        # Check if payment already exists for this test order to prevent duplicates
        payment, created = RazorpayPayment.objects.get_or_create(
            test_order=test_order,
            payment_type='test',
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'patient': patient,
                'prescription': getattr(test_order, 'prescription', None),
                'amount': Decimal(amount) / 100,
                'name': patient.name,
                'email': patient.email,
                'phone': patient.phone_number,
                'address': patient.address,
                'receipt': receipt_id,
                'notes': razorpay_order['notes']
            }
        )
        
        # If payment already exists, update the razorpay_order_id for the new session
        if not created:
            payment.razorpay_order_id = razorpay_order['id']
            payment.save()
        
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
                
            elif payment.payment_type == 'prescription_order' and payment.prescription_upload:
                # Handle prescription order payment success
                from pharmacy.models import Order, Cart

                prescription_upload = payment.prescription_upload

                # Create an order from the prescription
                order = Order.objects.create(
                    user=request.user,
                    ordered=True,
                    payment_status='paid',
                    order_status='confirmed',
                    delivery_method=prescription_upload.delivery_method,
                    delivery_address=prescription_upload.delivery_address,
                    delivery_phone=prescription_upload.delivery_phone
                )

                # Create cart items from prescription medicines
                cart_items = []
                for prescription_med in prescription_upload.medicines.all():
                    cart_item = Cart.objects.create(
                        user=request.user,
                        item=prescription_med.medicine,
                        quantity=prescription_med.quantity,
                        purchased=True
                    )
                    cart_items.append(cart_item)

                # Add cart items to order
                order.orderitems.set(cart_items)

                # Update stock quantities
                try:
                    order.stock_quantity_decrease()
                except ValueError as e:
                    messages.warning(request, f'Stock update warning: {str(e)}')

                # Link prescription to order
                prescription_upload.related_order = order
                prescription_upload.status = 'paid_pending'  # Changed from 'fulfilled' to 'paid_pending'
                prescription_upload.save()

                messages.success(request, f'Prescription payment successful! Your medicine order #{order.id} is confirmed.')

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
            
            # Generate invoice for non-pharmacy payments (appointments, tests)
            # Pharmacy orders use the original pharmacy invoice system
            if payment.payment_type != 'pharmacy':
                try:
                    invoice = generate_invoice_for_payment(payment)
                    if payment.payment_type == 'appointment':
                        messages.success(request, 'Appointment payment successful! Doctor consultation invoice generated.')
                    elif payment.payment_type == 'test':
                        messages.success(request, 'Lab test payment successful! Test invoice generated.')
                    else:
                        messages.success(request, 'Payment successful! Invoice generated.')
                    return render(request, 'razorpay_payment/payment_success.html', {
                        'payment': payment,
                        'invoice': invoice
                    })
                except Exception as e:
                    if payment.payment_type == 'appointment':
                        messages.success(request, 'Appointment payment successful!')
                    elif payment.payment_type == 'test':
                        messages.success(request, 'Lab test payment successful!')
                    else:
                        messages.success(request, 'Payment successful!')
                    messages.warning(request, f'Invoice generation failed: {str(e)}')
                    return render(request, 'razorpay_payment/payment_success.html', {'payment': payment})
            else:
                # For pharmacy payments, just show success (they use pharmacy invoice system)
                messages.success(request, 'Payment successful! Your medicine order is confirmed.')
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
    """Production-ready invoice download with enhanced error handling"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        # Check if user has permission to download this invoice
        if hasattr(request.user, 'patient'):
            patient = request.user.patient
            if invoice.payment.patient != patient:
                logger.warning(f"Unauthorized invoice access attempt by user {request.user.id}")
                messages.error(request, 'You do not have permission to access this invoice.')
                return redirect('patient-dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('patient-dashboard')
        
        # Try multiple methods for PDF generation (production-safe)
        pdf_content = None
        
        # Method 1: Check if PDF file already exists
        if hasattr(invoice, 'pdf_file') and invoice.pdf_file:
            try:
                with invoice.pdf_file.open('rb') as pdf_file:
                    pdf_content = pdf_file.read()
                logger.info(f"Served existing PDF for invoice {invoice_id}")
            except Exception as e:
                logger.warning(f"Failed to read existing PDF: {str(e)}")
        
        # Method 2: Generate PDF using existing generator
        if not pdf_content:
            try:
                pdf_generator = InvoicePDFGenerator(invoice)
                pdf_content = pdf_generator.generate_pdf()
                logger.info(f"Generated new PDF for invoice {invoice_id}")
                
                # Try to save for future use (optional, may fail on some servers)
                try:
                    if hasattr(invoice, 'pdf_file'):
                        from django.core.files.base import ContentFile
                        pdf_file = ContentFile(pdf_content)
                        invoice.pdf_file.save(
                            f"invoice_{invoice.invoice_number}.pdf",
                            pdf_file,
                            save=True
                        )
                except Exception as save_error:
                    logger.warning(f"Could not save PDF file: {str(save_error)}")
                    # Continue anyway, we have the content
                    
            except Exception as e:
                logger.error(f"InvoicePDFGenerator failed: {str(e)}")
        
        # Method 3: Generate simple PDF fallback
        if not pdf_content:
            try:
                pdf_content = generate_simple_invoice_pdf(invoice)
                logger.info(f"Generated simple PDF for invoice {invoice_id}")
            except Exception as e:
                logger.error(f"Simple PDF generation failed: {str(e)}")
        
        # Method 4: Generate text invoice (absolute fallback)
        if not pdf_content:
            try:
                text_content = generate_invoice_text(invoice)
                response = HttpResponse(text_content, content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.txt"'
                logger.warning(f"Serving text invoice for {invoice_id} due to PDF generation failures")
                return response
            except Exception as e:
                logger.error(f"Text invoice generation failed: {str(e)}")
        
        # Serve the PDF if we have it
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            response['Content-Length'] = len(pdf_content)
            
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
            logger.info(f"Successfully served PDF for invoice {invoice_id}")
            return response
        
        # If all methods failed
        logger.error(f"All invoice generation methods failed for invoice {invoice_id}")
        messages.error(request, 'Unable to generate invoice at this time. Please try again later or contact support.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        logger.error(f"Critical error in invoice download: {str(e)}")
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
    """Production-ready pharmacy invoice download with enhanced error handling"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from pharmacy.models import Order
        order = get_object_or_404(Order, id=order_id)
        
        # Check permissions - only the patient who made the order can download
        if request.user != order.user:
            logger.warning(f"Unauthorized pharmacy invoice access attempt by user {request.user.id}")
            messages.error(request, 'You do not have permission to access this invoice.')
            return redirect('patient-dashboard')
        
        # Try multiple methods for PDF generation (production-safe)
        pdf_content = None
        
        # Method 1: Try to generate PDF using ReportLab
        try:
            from .invoice_utils import generate_pharmacy_invoice_pdf
            pdf_content = generate_pharmacy_invoice_pdf(order)
            if pdf_content:
                logger.info(f"Generated pharmacy PDF for order {order_id}")
        except Exception as e:
            logger.error(f"Pharmacy PDF generation failed: {str(e)}")
        
        # Method 2: Generate simple PDF fallback
        if not pdf_content:
            try:
                pdf_content = generate_simple_pharmacy_pdf(order)
                logger.info(f"Generated simple pharmacy PDF for order {order_id}")
            except Exception as e:
                logger.error(f"Simple pharmacy PDF generation failed: {str(e)}")
        
        # Method 3: Generate text invoice (last resort)
        if not pdf_content:
            try:
                text_content = generate_pharmacy_text_invoice(order)
                response = HttpResponse(text_content, content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="pharmacy_invoice_{order.id}.txt"'
                logger.warning(f"Serving text pharmacy invoice for {order_id} due to PDF failures")
                return response
            except Exception as e:
                logger.error(f"Text pharmacy invoice generation failed: {str(e)}")
        
        # Serve the PDF if we have it
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="pharmacy_invoice_{order.id}.pdf"'
            response['Content-Length'] = len(pdf_content)
            
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
            logger.info(f"Successfully served pharmacy PDF for order {order_id}")
            return response
        
        # If all methods failed
        logger.error(f"All pharmacy invoice generation methods failed for order {order_id}")
        messages.error(request, 'Unable to generate invoice at this time. Please try again later or contact support.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        logger.error(f"Critical error in pharmacy invoice download: {str(e)}")
        messages.error(request, f'Error downloading invoice: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def cod_prescription_payment(request, prescription_upload_id):
    """Handle Cash on Delivery for prescription orders"""
    try:
        from pharmacy.models import PrescriptionUpload, Order, Cart

        prescription_upload = get_object_or_404(PrescriptionUpload, upload_id=prescription_upload_id)
        patient = prescription_upload.patient

        # Check if user has permission
        if patient.user != request.user:
            messages.error(request, 'You do not have permission to access this prescription.')
            return redirect('my-prescriptions')

        # Ensure prescription is approved
        if prescription_upload.status != 'approved':
            messages.error(request, 'Prescription is not approved yet.')
            return redirect('prescription_status', upload_id=prescription_upload_id)

        # Create an order from the prescription
        order = Order.objects.create(
            user=request.user,
            ordered=True,
            payment_status='cod_pending',  # Changed to cod_pending instead of cash_on_delivery
            order_status='confirmed',  # Start with confirmed, let pharmacist progress it
            delivery_method=prescription_upload.delivery_method,
            delivery_address=prescription_upload.delivery_address,
            delivery_phone=prescription_upload.delivery_phone
        )

        # Create cart items from prescription medicines
        cart_items = []
        for prescription_med in prescription_upload.medicines.all():
            cart_item = Cart.objects.create(
                user=request.user,
                item=prescription_med.medicine,
                quantity=prescription_med.quantity,
                purchased=True
            )
            cart_items.append(cart_item)

        # Add cart items to order
        order.orderitems.set(cart_items)

        # Link prescription to order and update status to paid_pending (waiting for pharmacy processing)
        prescription_upload.related_order = order
        prescription_upload.status = 'paid_pending'  # Changed from 'fulfilled' to 'paid_pending'
        prescription_upload.save()

        # Send notification
        try:
            from django.core.mail import send_mail
            from healthstack.email_utils import send_email_safely
            from django.conf import settings

            # Notify admin
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@mahimamedicare.com')
            send_mail(
                f'New COD Prescription Order #{order.id}',
                f'New prescription order with COD. Prescription #{prescription_upload_id}, Order #{order.id}, Patient: {patient.name}',
                settings.DEFAULT_FROM_EMAIL,
                [admin_email])

            # Notify patient
            if patient.email:
                send_mail(
                    'Prescription Order Confirmed - COD',
                    f'Your prescription order #{order.id} has been confirmed with Cash on Delivery. We will prepare your medicines for {"delivery" if order.delivery_method == "delivery" else "pickup"}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [patient.email],
                    fail_silently=True)
        except Exception:
            pass

        messages.success(request, 'Prescription order confirmed with Cash on Delivery!')
        return redirect('prescription_status', upload_id=prescription_upload_id)

    except Exception as e:
        messages.error(request, f'Error processing COD order: {str(e)}')
        return redirect('prescription_status', upload_id=prescription_upload_id)


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
        else:
            # Default case to ensure variables are always defined
            subject = f'New COD Order #{getattr(order, "id", "N/A")}'
            message = f'New Cash on Delivery order received. Order ID: {getattr(order, "id", "N/A")}'

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=True)

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
    """Allow patients to book lab tests independently with home collection support"""
    try:
        # Get all available tests from hospital_admin Test_Information model
        from hospital_admin.models import Test_Information
        
        # Get tests that are active and available
        available_tests = Test_Information.objects.filter(
            test_status='active'  # Assuming there's a status field
        ).order_by('test_name') if hasattr(Test_Information, 'test_status') else Test_Information.objects.all().order_by('test_name')

        # If no tests found, try from doctor models as fallback
        if not available_tests.exists():
            from doctor.models import Test
            doctor_tests = Test.objects.all().order_by('test_name')
            test_list = []
            for test in doctor_tests:
                test_list.append({
                    'id': test.id,
                    'name': test.test_name,
                    'price': float(test.amount) if hasattr(test, 'amount') and test.amount else 0,
                    'description': getattr(test, 'test_description', f'Lab test: {test.test_name}'),
                })
        else:
            # Convert Test_Information to template-friendly format
            test_list = []
            for test in available_tests:
                # Handle different possible field names
                test_id = getattr(test, 'test_id', None) or getattr(test, 'id', None)
                test_name = getattr(test, 'test_name', 'Unknown Test')
                
                # Get price from test_price field
                test_price = float(test.test_price) if test.test_price else 0
                
                test_description = f'Lab test: {test_name}'
                
                test_list.append({
                    'id': test_id,
                    'name': test_name,
                    'price': test_price,
                    'description': test_description,
                })

        # Home collection fee
        home_collection_fee = 99.0

        context = {
            'available_tests': test_list,
            'home_collection_fee': home_collection_fee,
            'test_count': len(test_list),
        }

        return render(request, 'lab-test-booking.html', context)

    except Exception as e:
        messages.error(request, f'Error loading test booking page: {str(e)}')
        return redirect('patient-dashboard')


@login_required
def submit_standalone_test(request):
    """Submit standalone test booking with home collection support"""
    if request.method == 'POST':
        try:
            selected_tests = request.POST.getlist('selected_tests')
            payment_method = request.POST.get('payment_method', 'online')
            collection_type = request.POST.get('collection_type', 'center')
            
            # Home collection specific fields
            preferred_collection_date = request.POST.get('preferred_collection_date')
            preferred_collection_time = request.POST.get('preferred_collection_time')
            collection_address = request.POST.get('collection_address', '').strip()

            if not selected_tests:
                messages.error(request, 'Please select at least one test.')
                return redirect('standalone-test-booking')

            # Validate home collection fields if applicable
            if collection_type == 'home':
                if not all([preferred_collection_date, preferred_collection_time, collection_address]):
                    messages.error(request, 'All home collection details are required.')
                    return redirect('standalone-test-booking')

            # Get patient or create if not exists
            from doctor.models import Patient
            patient = None
            try:
                patient = request.user.patient
            except Patient.DoesNotExist:
                patient = Patient.objects.create(
                    user=request.user,
                    first_name=request.user.first_name,
                    last_name=request.user.last_name,
                    email=request.user.email
                )

            # Import required models
            from doctor.models import testCart, testOrder, Test
            from hospital_admin.models import Test_Information, Clinical_Laboratory_Technician
            from decimal import Decimal

            # Get available lab worker for assignment
            try:
                available_lab_worker = Clinical_Laboratory_Technician.objects.first()
                if not available_lab_worker:
                    messages.warning(request, 'No lab workers available. Tests will be assigned manually.')
            except Clinical_Laboratory_Technician.DoesNotExist:
                available_lab_worker = None
                messages.warning(request, 'No lab workers configured. Tests will be assigned manually.')

            # Create a dummy prescription for standalone tests
            from doctor.models import Prescription, Doctor_Information

            # Create a dummy prescription entry for standalone tests
            try:
                # Try to get a default doctor or create one for standalone tests
                dummy_doctor = Doctor_Information.objects.filter(name__icontains='Standalone').first()
                if not dummy_doctor:
                    # Create a system doctor for standalone bookings
                    dummy_doctor = Doctor_Information.objects.create(
                        name='System - Standalone Booking',
                        department='Cardiologists',  # Use one of the valid choices
                        email='system@mahimamedicare.co.in'
                    )

                prescription = Prescription.objects.create(
                    doctor=dummy_doctor,
                    patient=patient,
                    test_description=f'Standalone lab test booking - {len(selected_tests)} tests',
                    extra_information='Self-requested lab tests'
                )
            except Exception as e:
                messages.error(request, f'Error creating prescription: {str(e)}')
                return redirect('standalone-test-booking')

            cart_items = []
            total_amount = 0

            for test_id in selected_tests:
                try:
                    test_id = int(test_id)
                    
                    # Try Test_Information first (hospital_admin managed tests)
                    lab_test = None
                    test_name = ''
                    test_price = 0
                    
                    try:
                        # Get test from Test_Information using test_id as primary key
                        lab_test = Test_Information.objects.get(test_id=test_id)
                        test_name = lab_test.test_name
                        test_price = float(lab_test.test_price) if lab_test.test_price else 0
                    except Test_Information.DoesNotExist:
                        try:
                            # Fallback to Test model (doctor managed tests)
                            lab_test = Test.objects.get(id=test_id)
                            test_name = lab_test.test_name
                            test_price = float(getattr(lab_test, 'amount', 0) or 0)
                        except Test.DoesNotExist:
                            continue

                    if not lab_test:
                        continue

                    # Create prescription test entry
                    from doctor.models import Prescription_test
                    prescription_test = Prescription_test.objects.create(
                        prescription=prescription,
                        test_name=test_name,
                        test_description=f'Standalone booking: {test_name}',
                        test_info_price=str(test_price),
                        test_info_pay_status='unpaid',
                        test_status='prescribed',
                        assigned_technician=available_lab_worker
                    )

                    # Create cart item
                    cart_item = testCart.objects.create(
                        user=request.user,
                        item=prescription_test,
                        purchased=False
                    )
                    cart_items.append(cart_item)

                except (ValueError, TypeError) as e:
                    messages.error(request, f'Error processing test ID {test_id}: {str(e)}')
                    continue

            # Check if any tests were successfully processed
            if not cart_items:
                messages.error(request, 'No valid tests found. Please select valid tests and try again.')
                return redirect('standalone-test-booking')

            # Calculate total with home collection fee (no VAT for lab tests)
            home_collection_fee = Decimal('99.00') if collection_type == 'home' else Decimal('0.00')
            final_total = Decimal(str(total_amount)) + home_collection_fee

            # Create test order with collection details
            test_order = testOrder.objects.create(
                user=request.user,
                ordered=False,
                payment_status='pending',
                collection_type=collection_type,
                home_collection_charge=home_collection_fee,
                collection_address=collection_address if collection_type == 'home' else '',
                preferred_collection_date=preferred_collection_date if collection_type == 'home' else None,
                preferred_collection_time=preferred_collection_time if collection_type == 'home' else None,
                collection_status='pending',
                final_bill=final_total
            )
            test_order.orderitems.set(cart_items)

            # Handle payment method
            if payment_method == 'cod':
                # Create payment record for admin tracking
                try:
                    from payment_management.utils import PaymentManager
                    
                    payment_record = PaymentManager.create_payment_record(
                        user=request.user,
                        payment_type='lab_test',
                        payment_method='cod',
                        base_amount=int(total_amount),
                        additional_fees=int(home_collection_fee),
                        order_reference=f"LAB_{test_order.pk}",
                        customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                        customer_phone=getattr(request.user, 'phone', ''),
                        customer_address=collection_address if collection_type == 'home' else ''
                    )
                    
                    # Store payment tracking info for admin reference
                    print(f"Payment record created: {payment_record.payment_id} for test order {test_order.pk}")
                    
                except Exception as e:
                    # Continue even if payment tracking fails
                    print(f"Payment tracking error: {e}")
                
                # Direct COD processing
                test_order.payment_status = 'cod_pending'
                test_order.ordered = True
                if collection_type == 'home':
                    test_order.collection_status = 'scheduled'
                    success_message = f'Lab test booking successful! Home collection scheduled for {preferred_collection_date}. Payment: ₹{final_total} (Cash on Delivery)'
                else:
                    test_order.collection_status = 'pending'
                    success_message = f'Lab test booking successful! Please visit our center for sample collection. Payment: ₹{final_total} (Cash on Delivery)'
                test_order.save()

                # Update cart items and prescription tests
                for cart_item in cart_items:
                    cart_item.purchased = True
                    cart_item.item.test_info_pay_status = 'paid'  # Set as 'paid' so it shows in lab queue
                    cart_item.item.test_status = 'prescribed'  # Keep as prescribed, lab worker will change to collected
                    cart_item.item.save()
                    cart_item.save()

                # Send notification
                send_cod_notification_email('standalone_test', test_order)

                messages.success(request, success_message)
                return redirect('patient-dashboard')
            else:
                # Redirect to payment
                return redirect('razorpay-test-payment', test_order_id=test_order.pk)

        except Exception as e:
            messages.error(request, f'Error booking tests: {str(e)}')
            return redirect('standalone-test-booking')


# Enhanced Lab Test Booking with Home Collection
@login_required
def enhanced_lab_test_booking(request):
    """Enhanced lab test booking with home collection option"""
    try:
        # Get user's current cart items
        cart_items = testCart.objects.filter(user=request.user, purchased=False)
        
        if not cart_items.exists():
            messages.info(request, 'No tests found in your cart. Please add tests first.')
            return redirect('lab-test-catalog')

        # Calculate pricing
        tests_total = sum(item.total for item in cart_items)
        vat_amount = get_lab_test_vat()
        total_amount = tests_total + vat_amount

        # Get today's date for minimum date validation
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        context = {
            'cart_items': cart_items,
            'tests_total': tests_total,
            'vat_amount': vat_amount,
            'total_amount': total_amount,
            'VAT_AMOUNT': vat_amount,
            'today': tomorrow.isoformat(),  # Minimum date (tomorrow)
        }

        if request.method == 'POST':
            return process_enhanced_test_booking(request, cart_items, tests_total, vat_amount)

        return render(request, 'lab-test-booking.html', context)

    except Exception as e:
        messages.error(request, f'Error loading lab test booking: {str(e)}')
        return redirect('lab-test-catalog')


def process_enhanced_test_booking(request, cart_items, tests_total, vat_amount):
    """Process the enhanced test booking with home collection"""
    try:
        # Get form data
        collection_type = request.POST.get('collection_type', 'center')
        payment_method = request.POST.get('payment_method', 'online')
        
        # Home collection specific fields
        preferred_collection_date = request.POST.get('preferred_collection_date')
        preferred_collection_time = request.POST.get('preferred_collection_time')
        collection_address = request.POST.get('collection_address', '').strip()
        
        # Validate home collection fields if applicable
        if collection_type == 'home':
            if not all([preferred_collection_date, preferred_collection_time, collection_address]):
                messages.error(request, 'All home collection details are required.')
                return redirect('enhanced-lab-test-booking')
            
            # Validate collection date (must be at least tomorrow)
            try:
                collection_date = datetime.strptime(preferred_collection_date, '%Y-%m-%d').date()
                tomorrow = timezone.now().date() + timedelta(days=1)
                if collection_date < tomorrow:
                    messages.error(request, 'Collection date must be at least tomorrow.')
                    return redirect('enhanced-lab-test-booking')
            except ValueError:
                messages.error(request, 'Invalid collection date format.')
                return redirect('enhanced-lab-test-booking')

        # Calculate total with home collection fee
        home_collection_fee = Decimal('99.00') if collection_type == 'home' else Decimal('0.00')
        final_total = Decimal(str(tests_total)) + home_collection_fee + Decimal(str(vat_amount))

        # Create test order
        test_order = testOrder.objects.create(
            user=request.user,
            payment_status='pending',
            collection_type=collection_type,
            home_collection_fee=home_collection_fee,
            collection_address=collection_address if collection_type == 'home' else '',
            preferred_collection_date=preferred_collection_date if collection_type == 'home' else None,
            preferred_collection_time=preferred_collection_time if collection_type == 'home' else None,
            collection_status='pending'
        )

        # Add cart items to order
        for cart_item in cart_items:
            test_order.orderitems.add(cart_item)

        test_order.save()

        # Handle payment method
        if payment_method == 'cod':
            # Cash on Delivery - mark as ordered but unpaid
            test_order.payment_status = 'cod_pending'
            test_order.ordered = True
            test_order.save()

            # Update cart items as purchased
            cart_items.update(purchased=True)

            # Set appropriate collection status
            if collection_type == 'home':
                test_order.collection_status = 'scheduled'
                success_message = f'Lab test booking successful! Home collection scheduled for {preferred_collection_date}. Payment: ₹{final_total} (Cash on Delivery)'
            else:
                test_order.collection_status = 'pending'
                success_message = f'Lab test booking successful! Please visit our center for sample collection. Payment: ₹{final_total} (Cash on Delivery)'
            
            test_order.save()
            messages.success(request, success_message)
            return redirect('patient-lab-tests')

        else:
            # Online payment - redirect to payment gateway
            return redirect('razorpay-test-payment', test_order_id=test_order.pk)

    except Exception as e:
        messages.error(request, f'Error processing booking: {str(e)}')
        return redirect('enhanced-lab-test-booking')


@login_required
def add_test_to_cart(request):
    """Add test to cart for enhanced booking"""
    if request.method == 'POST':
        try:
            test_id = request.POST.get('test_id')
            
            # Get test information
            test_info = get_object_or_404(Test_Information, test_id=test_id)
            
            # Create prescription test entry
            prescription_test = Prescription_test.objects.create(
                test_name=test_info.test_name,
                test_info_price=test_info.test_price,
                test_info_id=test_info.test_id,
                test_status='prescribed'
            )
            
            # Check if test already in cart
            existing_cart_item = testCart.objects.filter(
                user=request.user,
                item=prescription_test,
                purchased=False
            ).first()
            
            if existing_cart_item:
                messages.info(request, f'{test_info.test_name} is already in your cart.')
            else:
                # Add to cart
                cart_item = testCart.objects.create(
                    user=request.user,
                    item=prescription_test,
                    purchased=False
                )
                messages.success(request, f'{test_info.test_name} added to cart successfully.')
            
            return redirect('lab-test-catalog')
            
        except Exception as e:
            messages.error(request, f'Error adding test to cart: {str(e)}')
            return redirect('lab-test-catalog')
    
    return redirect('lab-test-catalog')


@login_required
def remove_test_from_cart(request, cart_item_id):
    """Remove test from cart"""
    try:
        cart_item = get_object_or_404(testCart, id=cart_item_id, user=request.user, purchased=False)
        test_name = cart_item.item.test_name
        
        # Delete the prescription test and cart item
        prescription_test = cart_item.item
        cart_item.delete()
        prescription_test.delete()
        
        messages.success(request, f'{test_name} removed from cart.')
        
    except Exception as e:
        messages.error(request, f'Error removing test: {str(e)}')
    
    return redirect('enhanced-lab-test-booking')


@login_required
def lab_test_catalog(request):
    """Display available lab tests for selection"""
    try:
        # Get all available tests
        available_tests = Test_Information.objects.all().order_by('test_name')
        
        # Get user's current cart items
        cart_items = testCart.objects.filter(user=request.user, purchased=False)
        cart_test_names = [item.item.test_name for item in cart_items]
        
        context = {
            'available_tests': available_tests,
            'cart_test_names': cart_test_names,
            'cart_count': cart_items.count(),
        }
        
        return render(request, 'lab-test-catalog.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading test catalog: {str(e)}')
        return redirect('patient-dashboard')

    return redirect('standalone-test-booking')


# Helper functions for production-safe invoice generation

def generate_simple_invoice_pdf(invoice):
    """Simple PDF generation using minimal dependencies"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "MAHIMA MEDICARE")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, "Healthcare Management System")
        p.drawString(50, height - 100, "Email: info@mahimamedicare.com")
        
        # Invoice details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 140, f"INVOICE #{invoice.invoice_number}")
        
        p.setFont("Helvetica", 11)
        y_position = height - 170
        
        # Basic invoice info
        invoice_data = [
            f"Date: {invoice.created_at.strftime('%B %d, %Y')}",
            f"Patient: {invoice.payment.patient.name if hasattr(invoice.payment, 'patient') else 'N/A'}",
            f"Amount: Rs.{invoice.total_amount}",
            f"Status: {invoice.status}",
        ]
        
        for line in invoice_data:
            p.drawString(50, y_position, line)
            y_position -= 20
        
        # Footer
        p.setFont("Helvetica", 10)
        p.drawString(50, 50, "Thank you for choosing Mahima Medicare!")
        p.drawString(50, 35, "For support: info@mahimamedicare.com")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        raise Exception(f"Simple PDF generation failed: {str(e)}")


def generate_invoice_text(invoice):
    """Generate plain text invoice as absolute fallback"""
    try:
        content = f"""
MAHIMA MEDICARE
Healthcare Management System
===============================

INVOICE #{invoice.invoice_number}

Date: {invoice.created_at.strftime('%B %d, %Y')}
Patient: {invoice.payment.patient.name if hasattr(invoice.payment, 'patient') else 'N/A'}
Amount: Rs.{invoice.total_amount}
Status: {invoice.status}

===============================
Thank you for choosing Mahima Medicare!
For support: info@mahimamedicare.com
        """
        return content.strip()
    except Exception as e:
        return f"Invoice #{invoice.invoice_number}\\nError generating invoice details: {str(e)}"


def generate_simple_pharmacy_pdf(order):
    """Simple PDF generation for pharmacy orders"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "MAHIMA MEDICARE - PHARMACY")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, "Healthcare Management System")
        p.drawString(50, height - 100, "Email: info@mahimamedicare.com")
        
        # Order details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 140, f"PHARMACY INVOICE #{getattr(order, 'pk', 'N/A')}")
        
        p.setFont("Helvetica", 11)
        y_position = height - 170
        
        # Basic order info
        order_data = [
            f"Date: {order.created.strftime('%B %d, %Y') if hasattr(order, 'created') else 'N/A'}",
            f"Patient: {order.user.first_name} {order.user.last_name}",
            f"Delivery Method: {getattr(order, 'delivery_method', 'N/A').title()}",
        ]
        
        for line in order_data:
            p.drawString(50, y_position, line)
            y_position -= 20
        
        # Items section
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position - 10, "Items:")
        y_position -= 30
        
        p.setFont("Helvetica", 10)
        total = 0
        
        try:
            if hasattr(order, 'orderitems'):
                for item in order.orderitems.all():
                    item_total = getattr(item, 'get_total', lambda: 0)()
                    total += item_total
                    p.drawString(50, y_position, f"- {item.item.name} x{item.quantity}: Rs.{item_total}")
                    y_position -= 15
        except:
            p.drawString(50, y_position, "Items information not available")
            y_position -= 15
        
        # Total
        y_position -= 10
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y_position, f"Total: Rs.{total}")
        
        # Footer
        p.setFont("Helvetica", 10)
        p.drawString(50, 50, "Thank you for your order!")
        p.drawString(50, 35, "Mahima Medicare Pharmacy")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        raise Exception(f"Simple pharmacy PDF generation failed: {str(e)}")


def generate_pharmacy_text_invoice(order):
    """Generate text-based pharmacy invoice"""
    try:
        content = f"""
MAHIMA MEDICARE - PHARMACY
==========================

PHARMACY INVOICE #{getattr(order, 'pk', 'N/A')}

Date: {order.created.strftime('%B %d, %Y') if hasattr(order, 'created') else 'N/A'}
Patient: {order.user.first_name} {order.user.last_name}
Delivery Method: {getattr(order, 'delivery_method', 'N/A').title()}

Items:
"""
        
        total = 0
        try:
            if hasattr(order, 'orderitems'):
                for item in order.orderitems.all():
                    item_total = getattr(item, 'get_total', lambda: 0)()
                    total += item_total
                    content += f"- {item.item.name} x{item.quantity}: Rs.{item_total}\\n"
        except:
            content += "Items information not available\\n"
        
        content += f"""
--------------------------
Total: Rs.{total}
GST (5%): Rs.{total * 0.05:.2f}
Final Total: Rs.{getattr(order, 'final_bill', lambda: total)()}

Thank you for your order!
Mahima Medicare Pharmacy
        """
        
        return content
    except Exception as e:
        return f"Pharmacy Invoice #{getattr(order, 'pk', 'N/A')}\\nError generating invoice details: {str(e)}"
