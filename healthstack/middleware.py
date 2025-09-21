"""
Security and monitoring middleware for Mahima Medicare
"""

import logging
import time
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import re

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """Enhanced security middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Suspicious patterns
        self.suspicious_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'union.*select',
            r'drop.*table',
            r'insert.*into',
            r'delete.*from',
        ]
        super().__init__(get_response)

    def process_request(self, request):
        # Log all requests
        logger.info(f"Request: {request.method} {request.path} - User: {request.user} - IP: {self.get_client_ip(request)}")
        
        # Check for suspicious patterns
        if self.contains_suspicious_content(request):
            logger.warning(f"Suspicious request detected: {request.path} - IP: {self.get_client_ip(request)}")
            return HttpResponseForbidden("Suspicious request detected")
        
        # Rate limiting
        if self.is_rate_limited(request):
            logger.warning(f"Rate limit exceeded: {request.path} - IP: {self.get_client_ip(request)}")
            return HttpResponseForbidden("Rate limit exceeded")
        
        return None

    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Log response
        logger.info(f"Response: {response.status_code} for {request.path}")
        
        return response

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def contains_suspicious_content(self, request):
        """Check for suspicious patterns in request"""
        # Check GET parameters
        for key, value in request.GET.items():
            for pattern in self.suspicious_patterns:
                if re.search(pattern, str(value), re.IGNORECASE):
                    return True
        
        # Check POST data
        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, str(value), re.IGNORECASE):
                        return True
        
        return False

    def is_rate_limited(self, request):
        """Simple rate limiting"""
        ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{ip}"
        
        # Get current request count
        request_count = cache.get(cache_key, 0)
        
        # Allow 100 requests per minute
        if request_count > 100:
            return True
        
        # Increment counter
        cache.set(cache_key, request_count + 1, 60)  # 60 seconds
        return False


class SessionSecurityMiddleware(MiddlewareMixin):
    """Session security middleware"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check session timeout
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                    logout(request)
                    return redirect('login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Check for session hijacking
            current_ip = self.get_client_ip(request)
            session_ip = request.session.get('ip_address')
            
            if session_ip and session_ip != current_ip:
                logger.warning(f"Possible session hijacking: User {request.user} - Old IP: {session_ip} - New IP: {current_ip}")
                logout(request)
                return redirect('login')
            
            # Store IP in session
            request.session['ip_address'] = current_ip
        
        return None

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Performance monitoring middleware"""
    
    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests (> 2 seconds)
            if duration > 2.0:
                logger.warning(f"Slow request: {request.path} took {duration:.2f}s - User: {request.user}")
            
            # Add performance header
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """Maintenance mode middleware"""
    
    def process_request(self, request):
        # Check if maintenance mode is enabled
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        
        if maintenance_mode:
            # Allow superusers to access during maintenance
            if request.user.is_authenticated and request.user.is_superuser:
                return None
            
            # Allow access to maintenance page
            if request.path == '/maintenance/':
                return None
            
            # Redirect to maintenance page
            return redirect('/maintenance/')
        
        return None
