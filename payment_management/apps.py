# Payment Management App Configuration
from django.apps import AppConfig

class PaymentManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment_management'
    verbose_name = 'Payment Management System'
    
    def ready(self):
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass