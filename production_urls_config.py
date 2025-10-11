
# Add these to your razorpay_payment/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    
    # Production-ready invoice downloads
    path('invoice/download-prod/<int:invoice_id>/', views.download_invoice_production, name='download-invoice-prod'),
    path('pharmacy-invoice/download-prod/<int:order_id>/', views.download_pharmacy_invoice_production, name='download-pharmacy-invoice-prod'),
]
