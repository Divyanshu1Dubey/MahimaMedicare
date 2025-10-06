from django.urls import path
from . import views

urlpatterns = [
    # Payment creation URLs
    path('appointment/<int:appointment_id>/', views.create_appointment_payment, name='razorpay-appointment-payment'),
    path('pharmacy/<int:order_id>/', views.create_pharmacy_payment, name='razorpay-pharmacy-payment'),
    path('test/<int:test_order_id>/', views.create_test_payment, name='razorpay-test-payment'),
    path('prescription/<int:prescription_upload_id>/', views.create_prescription_payment, name='razorpay-prescription-payment'),

    # COD URLs
    path('cod/test/<int:test_order_id>/', views.cod_test_payment, name='cod-test-payment'),
    path('cod/pharmacy/<int:order_id>/', views.cod_pharmacy_payment, name='cod-pharmacy-payment'),
    path('cod/prescription/<int:prescription_upload_id>/', views.cod_prescription_payment, name='cod-prescription-payment'),

    # Patient standalone test booking (Original)
    path('book-test/', views.standalone_test_booking, name='standalone-test-booking'),
    path('book-test/submit/', views.submit_standalone_test, name='submit-standalone-test'),
    
    # Enhanced Lab Test Booking with Home Collection
    path('lab-tests/catalog/', views.lab_test_catalog, name='lab-test-catalog'),
    path('lab-tests/booking/', views.enhanced_lab_test_booking, name='enhanced-lab-test-booking'),
    path('lab-tests/add-to-cart/', views.add_test_to_cart, name='add-test-to-cart'),
    path('lab-tests/remove-from-cart/<int:cart_item_id>/', views.remove_test_from_cart, name='remove-test-from-cart'),
    
    # Payment callback URLs
    path('success/', views.payment_success, name='razorpay-payment-success'),
    path('failed/', views.payment_failed, name='razorpay-payment-failed'),
    
    # Webhook URL
    path('webhook/', views.razorpay_webhook, name='razorpay-webhook'),
    
    # Invoice URLs
    path('invoice/download/<int:invoice_id>/', views.download_invoice, name='download-invoice'),
    path('invoice/view/<int:invoice_id>/', views.view_invoice, name='view-invoice'),
    path('invoice/regenerate/<int:payment_id>/', views.regenerate_invoice, name='regenerate-invoice'),
    
    # Pharmacy Invoice URLs
    path('pharmacy-invoice/download/<int:order_id>/', views.download_pharmacy_invoice, name='download-pharmacy-invoice'),
    path('pharmacy-invoice/view/<int:order_id>/', views.view_pharmacy_invoice, name='view-pharmacy-invoice'),
]
