# Payment Management Admin Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import requests

from .models import PaymentRecord, PaymentVerificationLog, DailyPaymentSummary
from django.contrib.auth import get_user_model

User = get_user_model()

@staff_member_required
def payment_dashboard(request):
    """
    Main payment management dashboard for admin
    """
    today = timezone.now().date()
    
    # Today's Statistics
    today_payments = PaymentRecord.objects.filter(created_at__date=today)
    today_stats = {
        'total_payments': today_payments.count(),
        'total_amount': today_payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'verified_payments': today_payments.filter(is_admin_verified=True).count(),
        'pending_payments': today_payments.filter(status='pending').count(),
        'received_payments': today_payments.filter(status='received').count(),
    }
    
    # Recent Payments (Last 50)
    recent_payments = PaymentRecord.objects.select_related('user', 'admin_verified_by')[:50]
    
    # Pending Verifications
    pending_verifications = PaymentRecord.objects.filter(
        Q(status='received') & Q(is_admin_verified=False)
    ).select_related('user')[:20]
    
    # Payment Method Summary
    payment_methods = PaymentRecord.objects.filter(created_at__date=today).values(
        'payment_method'
    ).annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    # Payment Type Summary  
    payment_types = PaymentRecord.objects.filter(created_at__date=today).values(
        'payment_type'
    ).annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    context = {
        'today_stats': today_stats,
        'recent_payments': recent_payments,
        'pending_verifications': pending_verifications,
        'payment_methods': payment_methods,
        'payment_types': payment_types,
        'today': today,
    }
    
    return render(request, 'payment_management/dashboard.html', context)


@staff_member_required
def verify_payment(request, payment_id):
    """
    Verify a payment and mark it as admin verified
    """
    payment = get_object_or_404(PaymentRecord, payment_id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        # Store previous status for logging
        previous_status = payment.status
        
        if action == 'verify':
            payment.status = 'verified'
            payment.is_admin_verified = True
            payment.admin_verified_by = request.user
            payment.admin_verification_date = timezone.now()
            payment.admin_notes = admin_notes
            
            # If it's a Razorpay payment, verify with Razorpay API
            if payment.payment_method == 'online' and payment.razorpay_payment_id:
                razorpay_status = verify_razorpay_payment(payment.razorpay_payment_id)
                if razorpay_status:
                    payment.razorpay_response = razorpay_status
            
            messages.success(request, f'Payment {payment_id} has been verified successfully.')
            
        elif action == 'reject':
            payment.status = 'failed'
            payment.admin_notes = admin_notes
            messages.warning(request, f'Payment {payment_id} has been marked as failed.')
            
        elif action == 'mark_received':
            payment.status = 'received'
            payment.payment_received_at = timezone.now()
            payment.admin_notes = admin_notes
            messages.info(request, f'Payment {payment_id} has been marked as received.')
        
        payment.save()
        
        # Log the admin action
        PaymentVerificationLog.objects.create(
            payment_record=payment,
            admin_user=request.user,
            action_taken=action,
            previous_status=previous_status,
            new_status=payment.status,
            notes=admin_notes
        )
        
        return redirect('payment_management:payment_detail', payment_id=payment_id)
    
    return render(request, 'payment_management/verify_payment.html', {'payment': payment})


@staff_member_required
def payment_detail(request, payment_id):
    """
    Detailed view of a specific payment
    """
    payment = get_object_or_404(PaymentRecord, payment_id=payment_id)
    verification_logs = PaymentVerificationLog.objects.filter(
        payment_record=payment
    ).select_related('admin_user')
    
    # Razorpay verification if available
    razorpay_details = None
    if payment.razorpay_payment_id:
        razorpay_details = verify_razorpay_payment(payment.razorpay_payment_id)
    
    context = {
        'payment': payment,
        'verification_logs': verification_logs,
        'razorpay_details': razorpay_details,
    }
    
    return render(request, 'payment_management/payment_detail.html', context)


def verify_razorpay_payment(payment_id):
    """
    Verify payment directly with Razorpay API
    """
    try:
        # You'll need to add your Razorpay credentials
        from django.conf import settings
        
        # This is a mock - replace with actual Razorpay API call
        # razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # payment_details = razorpay_client.payment.fetch(payment_id)
        
        # Mock response for now
        payment_details = {
            'id': payment_id,
            'status': 'captured',  # or 'failed', 'created', etc.
            'amount': 50000,  # Amount in paise
            'method': 'card',
            'created_at': timezone.now().timestamp(),
        }
        
        return payment_details
        
    except Exception as e:
        print(f"Error verifying Razorpay payment: {e}")
        return None


@staff_member_required
def payment_reports(request):
    """
    Generate payment reports and analytics
    """
    # Date range filter
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Filter payments by date range
    payments = PaymentRecord.objects.filter(
        created_at__date__range=[start_date, end_date]
    )
    
    # Generate comprehensive report
    report_data = {
        'total_payments': payments.count(),
        'total_amount': payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'verified_amount': payments.filter(is_admin_verified=True).aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0,
        'pending_amount': payments.filter(status='pending').aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0,
        
        # By Payment Type
        'by_type': payments.values('payment_type').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        
        # By Payment Method
        'by_method': payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        
        # By Status
        'by_status': payments.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        
        # Daily breakdown
        'daily_breakdown': payments.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('day'),
    }
    
    context = {
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': (end_date - start_date).days,
    }
    
    return render(request, 'payment_management/reports.html', context)


@staff_member_required
def bulk_verify_payments(request):
    """
    Bulk verify multiple payments at once
    """
    if request.method == 'POST':
        payment_ids = request.POST.getlist('payment_ids')
        action = request.POST.get('action')
        
        if not payment_ids:
            messages.error(request, 'No payments selected.')
            return redirect('payment_management:dashboard')
        
        payments = PaymentRecord.objects.filter(payment_id__in=payment_ids)
        updated_count = 0
        
        for payment in payments:
            previous_status = payment.status
            
            if action == 'verify':
                payment.status = 'verified'
                payment.is_admin_verified = True
                payment.admin_verified_by = request.user
                payment.admin_verification_date = timezone.now()
                
            elif action == 'mark_received':
                payment.status = 'received'
                payment.payment_received_at = timezone.now()
            
            payment.save()
            updated_count += 1
            
            # Log the action
            PaymentVerificationLog.objects.create(
                payment_record=payment,
                admin_user=request.user,
                action_taken=f'bulk_{action}',
                previous_status=previous_status,
                new_status=payment.status,
                notes=f'Bulk action: {action}'
            )
        
        messages.success(request, f'{updated_count} payments have been {action}ed successfully.')
        
    return redirect('payment_management:dashboard')


@staff_member_required
def export_payments(request):
    """
    Export payments to CSV
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Payment ID', 'User', 'Type', 'Method', 'Amount', 'Status', 
        'Verified', 'Date Created', 'Razorpay ID', 'Customer Name', 'Phone'
    ])
    
    payments = PaymentRecord.objects.select_related('user').all()
    for payment in payments:
        writer.writerow([
            payment.payment_id,
            payment.user.username,
            payment.get_payment_type_display(),
            payment.get_payment_method_display(),
            payment.total_amount,
            payment.get_status_display(),
            'Yes' if payment.is_admin_verified else 'No',
            payment.created_at.strftime('%Y-%m-%d %H:%M'),
            payment.razorpay_payment_id or '',
            payment.customer_name,
            payment.customer_phone,
        ])
    
    return response