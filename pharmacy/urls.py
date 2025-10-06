from unicodedata import name
from django.urls import path
from . import views
from . import api_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# from . --> same directory
# Views functions and urls must be linked. # of views == # of urls
# App URL file - urls related to hospital


urlpatterns = [
    path('', views.pharmacy_shop, name='pharmacy_shop'),  # Main pharmacy page
    path('shop/', views.pharmacy_shop, name='pharmacy-shop'),  # Alternative shop URL
    path('product-single/<int:pk>/', views.pharmacy_single_product, name='product-single'),
    path('cart/', views.cart_view, name='pharmacy-cart'),
    path('checkout/', views.checkout_view, name='pharmacy-checkout'),
    path('my-orders/', views.my_orders, name='pharmacy-my-orders'),
    path('remove-item/<int:pk>/', views.remove_from_cart, name='remove-item'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('increase-item/<int:pk>/', views.increase_cart, name='increase-item'),
    path('decrease-item/<int:pk>/', views.decrease_cart, name='decrease-item'),
    
    # Prescription upload URLs
    path('upload-prescription/', views.upload_prescription, name='upload-prescription'),
    path('prescription-status/<int:upload_id>/', views.prescription_status, name='prescription_status'),
    path('my-prescriptions/', views.my_prescriptions, name='my-prescriptions'),
    path('prescription-to-cart/<int:prescription_upload_id>/', views.prescription_to_cart, name='prescription-to-cart'),
    
    # AJAX endpoints
    path('ajax/medicine-search/', views.ajax_medicine_search, name='ajax-medicine-search'),

    # Doctor prescription integration URLs
    path('doctor-prescriptions/', views.doctor_prescriptions, name='doctor-prescriptions'),
    path('prescription-to-pharmacy/<int:prescription_id>/', views.prescription_to_pharmacy, name='prescription-to-pharmacy'),

    # Pharmacist prescription management URLs
    path('pharmacist/prescriptions/', views.pharmacist_prescriptions, name='pharmacist_prescriptions'),
    path('pharmacist/review-prescription/<int:upload_id>/', views.review_prescription, name='review_prescription'),

    # API endpoints for medicine management
    path('api/fetch-hsn/', api_views.fetch_hsn_code_ajax, name='fetch-hsn-ajax'),
    path('api/composition-suggestions/', api_views.get_composition_suggestions_ajax, name='composition-suggestions'),
    path('api/search-medicines/', api_views.search_existing_medicines, name='search-medicines-ajax'),
    
    # Prescription payment URLs (redirects to Razorpay)
    path('prescription-payment/<int:prescription_upload_id>/', views.prescription_payment_redirect, name='prescription-payment-redirect'),
]
    


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)