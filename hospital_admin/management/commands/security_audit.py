"""
Security audit management command for Mahima Medicare
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import os
import hashlib
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Perform comprehensive security audit'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send security audit report via email',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix security issues where possible',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('🔒 Starting Security Audit...'))
            
            audit_results = {
                'timestamp': timezone.now(),
                'checks': [],
                'vulnerabilities': [],
                'recommendations': [],
                'score': 0,
                'max_score': 0
            }
            
            # Run security checks
            self.check_django_settings(audit_results, options['fix'])
            self.check_user_security(audit_results, options['fix'])
            self.check_file_permissions(audit_results, options['fix'])
            self.check_database_security(audit_results)
            self.check_session_security(audit_results)
            self.check_password_policies(audit_results)
            self.check_suspicious_activity(audit_results)
            
            # Calculate security score
            if audit_results['max_score'] > 0:
                score_percentage = (audit_results['score'] / audit_results['max_score']) * 100
            else:
                score_percentage = 0
            
            # Display results
            self.display_audit_results(audit_results, score_percentage)
            
            # Send email if requested
            if options['email']:
                self.send_audit_report(audit_results, score_percentage)
            
            # Set exit code based on security score
            if score_percentage < 70:
                self.stdout.write(self.style.ERROR('❌ Security audit failed - Score too low'))
                exit(1)
            elif score_percentage < 85:
                self.stdout.write(self.style.WARNING('⚠️ Security audit passed with warnings'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Security audit passed'))
                
        except Exception as e:
            logger.error(f'Security audit failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Security audit failed: {str(e)}'))

    def check_django_settings(self, results, fix_issues):
        """Check Django security settings"""
        self.stdout.write('Checking Django security settings...')
        
        checks = [
            ('DEBUG', not settings.DEBUG, 'DEBUG should be False in production', 10),
            ('SECRET_KEY', len(settings.SECRET_KEY) >= 50, 'SECRET_KEY should be at least 50 characters', 10),
            ('ALLOWED_HOSTS', bool(settings.ALLOWED_HOSTS), 'ALLOWED_HOSTS should be configured', 8),
            ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False), 'SSL redirect should be enabled', 8),
            ('SESSION_COOKIE_SECURE', getattr(settings, 'SESSION_COOKIE_SECURE', False), 'Secure session cookies should be enabled', 6),
            ('CSRF_COOKIE_SECURE', getattr(settings, 'CSRF_COOKIE_SECURE', False), 'Secure CSRF cookies should be enabled', 6),
            ('X_FRAME_OPTIONS', hasattr(settings, 'X_FRAME_OPTIONS'), 'X-Frame-Options should be set', 5),
        ]
        
        for check_name, passed, description, points in checks:
            results['max_score'] += points
            if passed:
                results['score'] += points
                results['checks'].append(f'✅ {description}')
            else:
                results['vulnerabilities'].append(f'❌ {description}')
                if check_name == 'DEBUG' and fix_issues:
                    results['recommendations'].append('Set DEBUG = False in production settings')

    def check_user_security(self, results, fix_issues):
        """Check user account security"""
        self.stdout.write('Checking user account security...')
        
        # Check for weak passwords
        weak_passwords = ['password', '123456', 'admin', 'test']
        users_with_weak_passwords = []
        
        for user in User.objects.all():
            if user.check_password('password') or user.check_password('123456'):
                users_with_weak_passwords.append(user.username)
        
        results['max_score'] += 10
        if not users_with_weak_passwords:
            results['score'] += 10
            results['checks'].append('✅ No users with common weak passwords found')
        else:
            results['vulnerabilities'].append(f'❌ {len(users_with_weak_passwords)} users with weak passwords')
            if fix_issues:
                # Force password reset for users with weak passwords
                for username in users_with_weak_passwords:
                    user = User.objects.get(username=username)
                    user.set_unusable_password()
                    user.save()
                results['recommendations'].append('Forced password reset for users with weak passwords')
        
        # Check for inactive superusers
        inactive_superusers = User.objects.filter(is_superuser=True, is_active=False).count()
        results['max_score'] += 5
        if inactive_superusers == 0:
            results['score'] += 5
            results['checks'].append('✅ No inactive superuser accounts')
        else:
            results['vulnerabilities'].append(f'❌ {inactive_superusers} inactive superuser accounts found')
        
        # Check for users without recent login
        old_threshold = timezone.now() - timedelta(days=90)
        old_users = User.objects.filter(
            last_login__lt=old_threshold,
            is_active=True
        ).exclude(last_login__isnull=True).count()
        
        results['max_score'] += 5
        if old_users < 5:
            results['score'] += 5
            results['checks'].append('✅ Most users have recent login activity')
        else:
            results['vulnerabilities'].append(f'❌ {old_users} users haven\'t logged in for 90+ days')

    def check_file_permissions(self, results, fix_issues):
        """Check file and directory permissions"""
        self.stdout.write('Checking file permissions...')
        
        critical_files = [
            settings.BASE_DIR / 'manage.py',
            settings.BASE_DIR / '.env',
            settings.BASE_DIR / 'db.sqlite3',
        ]
        
        permission_issues = []
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                file_mode = oct(file_stat.st_mode)[-3:]
                
                # Check if file is world-readable/writable
                if file_mode.endswith('7') or file_mode.endswith('6'):
                    permission_issues.append(f'{file_path} has overly permissive permissions: {file_mode}')
                    
                    if fix_issues:
                        os.chmod(file_path, 0o600)  # Read/write for owner only
        
        results['max_score'] += 8
        if not permission_issues:
            results['score'] += 8
            results['checks'].append('✅ File permissions are secure')
        else:
            results['vulnerabilities'].extend([f'❌ {issue}' for issue in permission_issues])
            if fix_issues:
                results['recommendations'].append('Fixed file permissions for critical files')

    def check_database_security(self, results):
        """Check database security"""
        self.stdout.write('Checking database security...')
        
        # Check if using SQLite in production
        db_engine = settings.DATABASES['default']['ENGINE']
        
        results['max_score'] += 10
        if 'sqlite' not in db_engine.lower():
            results['score'] += 10
            results['checks'].append('✅ Using production-grade database')
        else:
            results['vulnerabilities'].append('❌ Using SQLite in production (not recommended)')
            results['recommendations'].append('Consider migrating to PostgreSQL or MySQL for production')
        
        # Check database backup
        results['max_score'] += 5
        backup_dir = getattr(settings, 'BACKUP_ROOT', None)
        if backup_dir and os.path.exists(backup_dir):
            results['score'] += 5
            results['checks'].append('✅ Database backup system configured')
        else:
            results['vulnerabilities'].append('❌ No database backup system found')
            results['recommendations'].append('Set up automated database backups')

    def check_session_security(self, results):
        """Check session security settings"""
        self.stdout.write('Checking session security...')
        
        session_checks = [
            ('SESSION_COOKIE_AGE', settings.SESSION_COOKIE_AGE <= 3600, 'Session timeout should be reasonable (≤1 hour)', 5),
            ('SESSION_COOKIE_HTTPONLY', getattr(settings, 'SESSION_COOKIE_HTTPONLY', True), 'Session cookies should be HTTP-only', 5),
            ('SESSION_COOKIE_SAMESITE', getattr(settings, 'SESSION_COOKIE_SAMESITE', None) is not None, 'Session cookies should have SameSite attribute', 3),
        ]
        
        for check_name, passed, description, points in session_checks:
            results['max_score'] += points
            if passed:
                results['score'] += points
                results['checks'].append(f'✅ {description}')
            else:
                results['vulnerabilities'].append(f'❌ {description}')

    def check_password_policies(self, results):
        """Check password policy enforcement"""
        self.stdout.write('Checking password policies...')
        
        # Check if password validators are configured
        password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        
        results['max_score'] += 8
        if len(password_validators) >= 3:
            results['score'] += 8
            results['checks'].append('✅ Strong password validation configured')
        else:
            results['vulnerabilities'].append('❌ Insufficient password validation rules')
            results['recommendations'].append('Configure comprehensive password validators')

    def check_suspicious_activity(self, results):
        """Check for suspicious user activity"""
        self.stdout.write('Checking for suspicious activity...')
        
        # Check for multiple failed login attempts (if logging is available)
        # This is a placeholder - implement based on your logging system
        
        # Check for users created recently
        recent_threshold = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(date_joined__gte=recent_threshold).count()
        
        results['max_score'] += 5
        if recent_users < 10:  # Adjust threshold based on your needs
            results['score'] += 5
            results['checks'].append('✅ Normal user registration activity')
        else:
            results['vulnerabilities'].append(f'❌ High number of recent user registrations: {recent_users}')
            results['recommendations'].append('Review recent user registrations for suspicious activity')

    def display_audit_results(self, results, score_percentage):
        """Display audit results"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🔒 SECURITY AUDIT REPORT'))
        self.stdout.write('='*60)
        self.stdout.write(f"Timestamp: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"Security Score: {results['score']}/{results['max_score']} ({score_percentage:.1f}%)")
        
        if score_percentage >= 85:
            self.stdout.write(self.style.SUCCESS(f"Overall Rating: EXCELLENT 🟢"))
        elif score_percentage >= 70:
            self.stdout.write(self.style.WARNING(f"Overall Rating: GOOD 🟡"))
        else:
            self.stdout.write(self.style.ERROR(f"Overall Rating: NEEDS IMPROVEMENT 🔴"))
        
        self.stdout.write('\n📋 SECURITY CHECKS PASSED:')
        for check in results['checks']:
            self.stdout.write(f"  {check}")
        
        if results['vulnerabilities']:
            self.stdout.write('\n⚠️ VULNERABILITIES FOUND:')
            for vuln in results['vulnerabilities']:
                self.stdout.write(self.style.ERROR(f"  {vuln}"))
        
        if results['recommendations']:
            self.stdout.write('\n💡 RECOMMENDATIONS:')
            for rec in results['recommendations']:
                self.stdout.write(f"  • {rec}")
        
        self.stdout.write('\n' + '='*60)

    def send_audit_report(self, results, score_percentage):
        """Send audit report via email"""
        try:
            subject = f"Mahima Medicare - Security Audit Report ({results['timestamp'].strftime('%Y-%m-%d')})"
            
            # Determine status emoji
            if score_percentage >= 85:
                status_emoji = "🟢 EXCELLENT"
            elif score_percentage >= 70:
                status_emoji = "🟡 GOOD"
            else:
                status_emoji = "🔴 NEEDS IMPROVEMENT"
            
            message = f"""
Security Audit Report - Mahima Medicare Healthcare System
Generated: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

SECURITY SCORE: {results['score']}/{results['max_score']} ({score_percentage:.1f}%)
OVERALL RATING: {status_emoji}

SECURITY CHECKS PASSED:
{chr(10).join([f"• {check}" for check in results['checks']])}

VULNERABILITIES FOUND:
{chr(10).join([f"• {vuln}" for vuln in results['vulnerabilities']]) if results['vulnerabilities'] else "• None"}

RECOMMENDATIONS:
{chr(10).join([f"• {rec}" for rec in results['recommendations']]) if results['recommendations'] else "• None"}

This is an automated security audit report.
Please review and address any vulnerabilities found.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['admin@mahimamedicare.com'],  # Update with actual admin email
                fail_silently=False,
            )
            
            self.stdout.write('Security audit report sent via email')
            
        except Exception as e:
            logger.error(f'Failed to send security audit report: {str(e)}')
            self.stdout.write(f'Failed to send email: {str(e)}')
