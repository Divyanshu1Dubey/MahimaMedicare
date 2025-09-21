"""
API monitoring and analytics for Mahima Medicare
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json
import logging

from hospital.models import Patient, User
from doctor.models import Doctor_Information, Report, Appointment
from hospital_admin.models import Clinical_Laboratory_Technician
from pharmacy.models import Medicine
from razorpay_payment.models import RazorpayPayment

logger = logging.getLogger(__name__)

class SystemStatsAPI(View):
    """API for system statistics"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        try:
            # Only allow admin users
            if not (request.user.is_superuser or request.user.is_admin):
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Get date ranges
            now = timezone.now()
            today = now.date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # User statistics
            total_users = User.objects.count()
            active_users_today = User.objects.filter(last_login__date=today).count()
            new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
            
            # Patient statistics
            total_patients = Patient.objects.count()
            new_patients_week = Patient.objects.filter(
                user__date_joined__gte=week_ago
            ).count()
            
            # Doctor statistics
            total_doctors = Doctor_Information.objects.count()
            active_doctors = Doctor_Information.objects.filter(
                register_status='Accepted'
            ).count()
            
            # Lab statistics
            total_lab_techs = Clinical_Laboratory_Technician.objects.count()
            total_reports = Report.objects.count()
            pending_reports = Report.objects.filter(status='pending').count()
            completed_reports_week = Report.objects.filter(
                status='completed',
                delivery_date__gte=week_ago
            ).count()
            
            # Appointment statistics
            total_appointments = Appointment.objects.count()
            upcoming_appointments = Appointment.objects.filter(
                appointment_date__gte=today,
                appointment_status__in=['pending', 'confirmed']
            ).count()
            
            # Payment statistics
            total_payments = RazorpayPayment.objects.filter(status='captured').count()
            total_revenue = sum([
                payment.amount for payment in 
                RazorpayPayment.objects.filter(status='captured')
            ])
            revenue_this_month = sum([
                payment.amount for payment in 
                RazorpayPayment.objects.filter(
                    status='captured',
                    created_at__gte=month_ago
                )
            ])
            
            # Medicine statistics
            total_medicines = Medicine.objects.count()
            low_stock_medicines = Medicine.objects.filter(quantity__lt=10).count()
            
            stats = {
                'users': {
                    'total': total_users,
                    'active_today': active_users_today,
                    'new_this_week': new_users_week,
                },
                'patients': {
                    'total': total_patients,
                    'new_this_week': new_patients_week,
                },
                'doctors': {
                    'total': total_doctors,
                    'active': active_doctors,
                },
                'lab': {
                    'technicians': total_lab_techs,
                    'total_reports': total_reports,
                    'pending_reports': pending_reports,
                    'completed_this_week': completed_reports_week,
                },
                'appointments': {
                    'total': total_appointments,
                    'upcoming': upcoming_appointments,
                },
                'payments': {
                    'total_transactions': total_payments,
                    'total_revenue': float(total_revenue),
                    'revenue_this_month': float(revenue_this_month),
                },
                'pharmacy': {
                    'total_medicines': total_medicines,
                    'low_stock': low_stock_medicines,
                },
                'timestamp': now.isoformat(),
            }
            
            return JsonResponse(stats)
            
        except Exception as e:
            logger.error(f"Error in SystemStatsAPI: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


class HealthCheckAPI(View):
    """API for health check"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'checks': {}
            }
            
            # Database connectivity
            try:
                User.objects.count()
                health_status['checks']['database'] = 'healthy'
            except Exception as e:
                health_status['checks']['database'] = 'unhealthy'
                health_status['status'] = 'unhealthy'
                logger.error(f"Database health check failed: {str(e)}")
            
            # Check critical services
            try:
                # Check if we can create a simple query
                Patient.objects.filter(pk=1).exists()
                health_status['checks']['patient_service'] = 'healthy'
            except Exception as e:
                health_status['checks']['patient_service'] = 'unhealthy'
                health_status['status'] = 'degraded'
            
            try:
                Report.objects.filter(pk=1).exists()
                health_status['checks']['lab_service'] = 'healthy'
            except Exception as e:
                health_status['checks']['lab_service'] = 'unhealthy'
                health_status['status'] = 'degraded'
            
            # Check for critical issues
            critical_issues = []
            
            # Check for too many pending reports
            pending_reports = Report.objects.filter(status='pending').count()
            if pending_reports > 50:
                critical_issues.append(f"High number of pending reports: {pending_reports}")
            
            # Check for low stock medicines
            low_stock = Medicine.objects.filter(quantity__lt=5).count()
            if low_stock > 0:
                critical_issues.append(f"Critical low stock medicines: {low_stock}")
            
            if critical_issues:
                health_status['issues'] = critical_issues
                if health_status['status'] == 'healthy':
                    health_status['status'] = 'warning'
            
            return JsonResponse(health_status)
            
        except Exception as e:
            logger.error(f"Error in HealthCheckAPI: {str(e)}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': 'Health check failed',
                'timestamp': timezone.now().isoformat()
            }, status=500)


class ReportAnalyticsAPI(View):
    """API for report analytics"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        try:
            # Only allow lab workers and admins
            if not (request.user.is_labworker or request.user.is_admin or request.user.is_superuser):
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Get date range from query params
            days = int(request.GET.get('days', 30))
            start_date = timezone.now().date() - timedelta(days=days)
            
            # Report status distribution
            status_distribution = Report.objects.filter(
                uploaded_at__date__gte=start_date
            ).values('status').annotate(count=Count('status'))
            
            # Reports by priority
            priority_distribution = Report.objects.filter(
                uploaded_at__date__gte=start_date
            ).values('priority').annotate(count=Count('priority'))
            
            # Daily report creation trend
            daily_reports = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                count = Report.objects.filter(uploaded_at__date=date).count()
                daily_reports.append({
                    'date': date.isoformat(),
                    'count': count
                })
            
            # Top performing technicians
            top_technicians = Report.objects.filter(
                uploaded_at__date__gte=start_date,
                assigned_technician__isnull=False
            ).values(
                'assigned_technician__name'
            ).annotate(
                completed_reports=Count('report_id', filter=Q(status='completed'))
            ).order_by('-completed_reports')[:5]
            
            analytics = {
                'period_days': days,
                'status_distribution': list(status_distribution),
                'priority_distribution': list(priority_distribution),
                'daily_trend': daily_reports,
                'top_technicians': list(top_technicians),
                'timestamp': timezone.now().isoformat(),
            }
            
            return JsonResponse(analytics)
            
        except Exception as e:
            logger.error(f"Error in ReportAnalyticsAPI: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


# URL patterns for API endpoints
from django.urls import path

api_urlpatterns = [
    path('stats/', SystemStatsAPI.as_view(), name='api-system-stats'),
    path('health/', HealthCheckAPI.as_view(), name='api-health-check'),
    path('reports/analytics/', ReportAnalyticsAPI.as_view(), name='api-report-analytics'),
]
