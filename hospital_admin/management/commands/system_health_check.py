"""
System health check command for Mahima Medicare
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from hospital.models import Patient
from doctor.models import Doctor_Information, Report
from hospital_admin.models import Clinical_Laboratory_Technician
from pharmacy.models import Medicine
import os
import psutil
import datetime
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Perform system health check and generate report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send health report via email',
        )

    def handle(self, *args, **options):
        try:
            health_report = self.generate_health_report()
            
            # Display report
            self.display_report(health_report)
            
            # Send email if requested
            if options['email']:
                self.send_health_report_email(health_report)
            
            self.stdout.write(
                self.style.SUCCESS('System health check completed successfully')
            )
            
        except Exception as e:
            logger.error(f'Health check failed: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Health check failed: {str(e)}')
            )

    def generate_health_report(self):
        """Generate comprehensive health report"""
        report = {
            'timestamp': datetime.datetime.now(),
            'database': self.check_database_health(),
            'system': self.check_system_resources(),
            'application': self.check_application_health(),
            'security': self.check_security_status(),
        }
        return report

    def check_database_health(self):
        """Check database connectivity and statistics"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_connected = True
        except Exception as e:
            db_connected = False
            logger.error(f'Database connection failed: {str(e)}')

        # Get database statistics
        try:
            stats = {
                'users': User.objects.count(),
                'patients': Patient.objects.count(),
                'doctors': Doctor_Information.objects.count(),
                'lab_technicians': Clinical_Laboratory_Technician.objects.count(),
                'reports': Report.objects.count(),
                'medicines': Medicine.objects.count(),
                'recent_reports': Report.objects.filter(
                    uploaded_at__gte=datetime.datetime.now() - datetime.timedelta(days=7)
                ).count(),
            }
        except Exception as e:
            stats = {'error': str(e)}

        return {
            'connected': db_connected,
            'statistics': stats,
        }

    def check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Database file size
            db_path = settings.DATABASES['default']['NAME']
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'disk_usage': disk_percent,
                'database_size_mb': round(db_size, 2),
                'status': 'healthy' if all([
                    cpu_percent < 80,
                    memory_percent < 80,
                    disk_percent < 90
                ]) else 'warning'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}

    def check_application_health(self):
        """Check application-specific health metrics"""
        try:
            # Check recent activity
            recent_logins = User.objects.filter(
                last_login__gte=datetime.datetime.now() - datetime.timedelta(days=1)
            ).count()
            
            # Check pending reports
            pending_reports = Report.objects.filter(status='pending').count()
            processing_reports = Report.objects.filter(status='processing').count()
            
            # Check low stock medicines
            low_stock_medicines = Medicine.objects.filter(quantity__lt=10).count()
            
            return {
                'recent_logins_24h': recent_logins,
                'pending_reports': pending_reports,
                'processing_reports': processing_reports,
                'low_stock_medicines': low_stock_medicines,
                'status': 'healthy'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}

    def check_security_status(self):
        """Check security-related settings"""
        security_checks = {
            'debug_mode': settings.DEBUG,
            'secret_key_set': bool(settings.SECRET_KEY),
            'allowed_hosts_configured': bool(settings.ALLOWED_HOSTS),
            'session_timeout': settings.SESSION_COOKIE_AGE,
        }
        
        # Security score
        security_issues = []
        if security_checks['debug_mode']:
            security_issues.append('DEBUG mode is enabled')
        
        if not security_checks['allowed_hosts_configured']:
            security_issues.append('ALLOWED_HOSTS not properly configured')
        
        return {
            'checks': security_checks,
            'issues': security_issues,
            'status': 'secure' if not security_issues else 'warning'
        }

    def display_report(self, report):
        """Display health report in console"""
        self.stdout.write(self.style.SUCCESS('\n=== MAHIMA MEDICARE SYSTEM HEALTH REPORT ==='))
        self.stdout.write(f"Generated: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Database Health
        self.stdout.write(self.style.HTTP_INFO('DATABASE HEALTH:'))
        db = report['database']
        status = '✓' if db['connected'] else '✗'
        self.stdout.write(f"  Connection: {status}")
        
        if 'statistics' in db and 'error' not in db['statistics']:
            stats = db['statistics']
            self.stdout.write(f"  Users: {stats['users']}")
            self.stdout.write(f"  Patients: {stats['patients']}")
            self.stdout.write(f"  Doctors: {stats['doctors']}")
            self.stdout.write(f"  Lab Technicians: {stats['lab_technicians']}")
            self.stdout.write(f"  Total Reports: {stats['reports']}")
            self.stdout.write(f"  Recent Reports (7 days): {stats['recent_reports']}")
            self.stdout.write(f"  Medicines: {stats['medicines']}")
        
        # System Resources
        self.stdout.write(self.style.HTTP_INFO('\nSYSTEM RESOURCES:'))
        sys = report['system']
        if 'error' not in sys:
            self.stdout.write(f"  CPU Usage: {sys['cpu_usage']}%")
            self.stdout.write(f"  Memory Usage: {sys['memory_usage']}%")
            self.stdout.write(f"  Disk Usage: {sys['disk_usage']:.1f}%")
            self.stdout.write(f"  Database Size: {sys['database_size_mb']} MB")
            self.stdout.write(f"  Status: {sys['status'].upper()}")
        
        # Application Health
        self.stdout.write(self.style.HTTP_INFO('\nAPPLICATION HEALTH:'))
        app = report['application']
        if 'error' not in app:
            self.stdout.write(f"  Recent Logins (24h): {app['recent_logins_24h']}")
            self.stdout.write(f"  Pending Reports: {app['pending_reports']}")
            self.stdout.write(f"  Processing Reports: {app['processing_reports']}")
            self.stdout.write(f"  Low Stock Medicines: {app['low_stock_medicines']}")
        
        # Security Status
        self.stdout.write(self.style.HTTP_INFO('\nSECURITY STATUS:'))
        sec = report['security']
        if sec['issues']:
            for issue in sec['issues']:
                self.stdout.write(self.style.WARNING(f"  ⚠ {issue}"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ No security issues detected"))

    def send_health_report_email(self, report):
        """Send health report via email"""
        try:
            subject = f"Mahima Medicare - System Health Report ({report['timestamp'].strftime('%Y-%m-%d')})"
            
            # Create email content
            message = f"""
System Health Report - Mahima Medicare Healthcare System
Generated: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

DATABASE HEALTH:
- Connection: {'✓ Connected' if report['database']['connected'] else '✗ Disconnected'}
- Total Users: {report['database']['statistics'].get('users', 'N/A')}
- Total Patients: {report['database']['statistics'].get('patients', 'N/A')}
- Total Reports: {report['database']['statistics'].get('reports', 'N/A')}

SYSTEM RESOURCES:
- CPU Usage: {report['system'].get('cpu_usage', 'N/A')}%
- Memory Usage: {report['system'].get('memory_usage', 'N/A')}%
- Disk Usage: {report['system'].get('disk_usage', 'N/A')}%
- Database Size: {report['system'].get('database_size_mb', 'N/A')} MB

APPLICATION HEALTH:
- Recent Logins (24h): {report['application'].get('recent_logins_24h', 'N/A')}
- Pending Reports: {report['application'].get('pending_reports', 'N/A')}
- Low Stock Medicines: {report['application'].get('low_stock_medicines', 'N/A')}

SECURITY STATUS:
{chr(10).join([f"- ⚠ {issue}" for issue in report['security']['issues']]) if report['security']['issues'] else "- ✓ No security issues detected"}

This is an automated system health report.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['admin@mahimamedicare.com'],  # Update with actual admin email
                fail_silently=False,
            )
            
            self.stdout.write('Health report email sent successfully')
            
        except Exception as e:
            logger.error(f'Failed to send health report email: {str(e)}')
            self.stdout.write(f'Failed to send email: {str(e)}')
