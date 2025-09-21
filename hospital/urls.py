from unicodedata import name
from django.urls import path
from . import views
from doctor import views as doctor_views
from django.conf import settings
from django.conf.urls.static import static
from .pres_pdf import prescription_pdf

urlpatterns = [
    # General hospital pages
    path('', views.hospital_home, name='hospital_home'),
    path('search/', views.search, name='search'),
    path('change-password/<int:pk>/', views.change_password, name='change-password'),
    path('add-billing/', views.add_billing, name='add-billing'),
    path('appointments/', views.appointments, name='appointments'),
    path('edit-billing/', views.edit_billing, name='edit-billing'),
    path('edit-prescription/', views.edit_prescription, name='edit-prescription'),
    path('patient-dashboard/', views.patient_dashboard, name='patient-dashboard'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('profile-settings/', views.profile_settings, name='profile-settings'),
    path('about-us/', views.about_us, name='about-us'),
    path('patient-register/', views.patient_register, name='patient-register'),
    path('logout/', views.logoutUser, name='logout'),
    path('multiple-hospital/', views.multiple_hospital, name='multiple-hospital'),

    # Chat
    path('chat/<int:pk>/', views.chat, name='chat'),
    path('chat-doctor/', views.chat_doctor, name='chat-doctor'),

    # Hospital profile & listings
    path('hospital-profile/<int:pk>/', views.hospital_profile, name='hospital-profile'),
    path('hospital-department-list/<int:pk>/', views.hospital_department_list, name='hospital-department-list'),
    path('hospital-doctor-list/<int:pk>/', views.hospital_doctor_list, name='hospital-doctor-list'),
    path('hospital-doctor-register/<int:pk>/', views.hospital_doctor_register, name='hospital-doctor-register'),

    # Reports
    path('view-report/<int:pk>/', views.view_report, name='view-report'),
    path('delete-report/<int:pk>/', views.delete_report, name='delete-report'),
    path('download-report-pdf/<int:report_id>/', views.download_report_pdf, name='download-report-pdf'),

    # Checkout & pharmacy
    path('checkout-payment/', views.checkout_payment, name='checkout-payment'),
    path('shop/', views.pharmacy_shop, name='pharmacy_shop'),

    # Data & testing
    path('data-table/', views.data_table, name='data-table'),
    path('testing/', views.testing, name='testing'),

    # ======= TEST CART FLOW =======
    # Show all tests in the cart for a prescription
    path('test-cart/<int:pk>/', views.test_cart, name='test-cart'),

    # Prescription view
    path('prescription-view/<int:pk>/', views.prescription_view, name='prescription-view'),

    # PDF download of prescription
    path('pres_pdf/<int:pk>/', views.prescription_pdf, name='pres_pdf'),

    # View a single test from prescription
    path('test-single/<int:pk>/', views.test_single, name='test-single'),

    # Remove a test from cart (use testCart.id)
    path('test-remove-cart/<int:pk>/', views.test_remove_cart, name='test-remove-cart'),

    # Add a test to cart (pass prescription_id and test_info_id)
    path(
    'test-add-to-cart/<int:prescription_id>/<str:test_info_id>/',
    views.test_add_to_cart,
    name='test-add-to-cart'
),

    # Delete prescription
    path('delete-prescription/<int:pk>/', views.delete_prescription, name='delete-prescription'),
]

# Static & media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)