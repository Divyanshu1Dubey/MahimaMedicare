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
    """Create Razorpay order for pharmacy payment"""
    try:
        order = get_object_or_404(Order, id=order_id)
        patient = order.user.patient
        
        # Calculate amount (convert to paise for Razorpay)
        amount = int(float(order.final_bill()) * 100)
        
        # Create Razorpay order
        receipt_id = generate_receipt_id('pharmacy', order_id)
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
            'payment': payment
        }
        
        return render(request, 'razorpay_payment/pharmacy_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}')
        return redirect('pharmacy_shop')

@login_required
def create_test_payment(request, test_order_id):
    """Create Razorpay order for test payment"""
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
            
        amount = int(float(total_bill) * 100)
        
        # Create Razorpay order
        receipt_id = generate_receipt_id('test', test_order_id)
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
            'payment': payment
        }
        
        return render(request, 'razorpay_payment/test_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error creating payment: {str(e)}')
        return redirect('patient-dashboard')

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
                payment.order.payment_status = 'paid'
                payment.order.save()
                
            elif payment.payment_type == 'test' and payment.test_order:
                payment.test_order.payment_status = 'paid'
                payment.test_order.save()
            
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


@login_required
def regenerate_invoice(request, payment_id):
    """Regenerate invoice for a payment (admin function)"""
    try:
        payment = get_object_or_404(RazorpayPayment, id=payment_id)
        
        # Check if invoice already exists
        if hasattr(payment, 'invoice'):
            # Delete existing invoice
            payment.invoice.delete()
        
        # Generate new invoice
        invoice = generate_invoice_for_payment(payment)
        
        messages.success(request, f'Invoice {invoice.invoice_number} regenerated successfully.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        messages.error(request, f'Error regenerating invoice: {str(e)}')
        return redirect('patient-dashboard')
