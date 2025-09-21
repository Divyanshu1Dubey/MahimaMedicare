"""
Custom error handlers for Mahima Medicare Healthcare System
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import traceback

logger = logging.getLogger(__name__)

def handler404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Resource not found',
            'status': 404,
            'message': 'The requested resource could not be found.'
        }, status=404)
    
    return render(request, 'errors/404.html', {
        'title': 'Page Not Found',
        'message': 'The page you are looking for could not be found.'
    }, status=404)

def handler500(request):
    """Custom 500 error handler"""
    logger.error(f"500 Error: {request.path} - User: {request.user}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal server error',
            'status': 500,
            'message': 'An internal server error occurred. Please try again later.'
        }, status=500)
    
    return render(request, 'errors/500.html', {
        'title': 'Server Error',
        'message': 'An internal server error occurred. Our team has been notified.'
    }, status=500)

def handler403(request, exception):
    """Custom 403 error handler"""
    logger.warning(f"403 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Access forbidden',
            'status': 403,
            'message': 'You do not have permission to access this resource.'
        }, status=403)
    
    return render(request, 'errors/403.html', {
        'title': 'Access Forbidden',
        'message': 'You do not have permission to access this page.'
    }, status=403)

def handler400(request, exception):
    """Custom 400 error handler"""
    logger.warning(f"400 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Bad request',
            'status': 400,
            'message': 'The request could not be understood by the server.'
        }, status=400)
    
    return render(request, 'errors/400.html', {
        'title': 'Bad Request',
        'message': 'The request could not be processed.'
    }, status=400)

class ErrorHandlingMixin:
    """Mixin for adding error handling to views"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if request.is_ajax() or request.content_type == 'application/json':
                return JsonResponse({
                    'error': 'An error occurred',
                    'message': 'Please try again later.'
                }, status=500)
            
            return render(request, 'errors/500.html', {
                'title': 'Server Error',
                'message': 'An error occurred while processing your request.'
            }, status=500)
