from django.urls import path
from . import views

urlpatterns = [
    # Payment creation URLs
    path('appointment/<int:appointment_id>/', views.create_appointment_payment, name='razorpay-appointment-payment'),
    path('pharmacy/<int:order_id>/', views.create_pharmacy_payment, name='razorpay-pharmacy-payment'),
    path('test/<int:test_order_id>/', views.create_test_payment, name='razorpay-test-payment'),
    
    # Payment callback URLs
    path('success/', views.payment_success, name='razorpay-payment-success'),
    path('failed/', views.payment_failed, name='razorpay-payment-failed'),
    
    # Webhook URL
    path('webhook/', views.razorpay_webhook, name='razorpay-webhook'),
    
    # Invoice URLs
    path('invoice/download/<int:invoice_id>/', views.download_invoice, name='download-invoice'),
    path('invoice/view/<int:invoice_id>/', views.view_invoice, name='view-invoice'),
    path('invoice/regenerate/<int:payment_id>/', views.regenerate_invoice, name='regenerate-invoice'),
]
