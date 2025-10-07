# Enhanced Lab Test URLs
from django.urls import path
from . import enhanced_lab_views

urlpatterns = [
    # Enhanced Lab Test Booking with Home Collection
    path('lab-tests/catalog/', enhanced_lab_views.lab_test_catalog, name='lab-test-catalog'),
    path('lab-tests/booking/', enhanced_lab_views.enhanced_lab_test_booking, name='enhanced-lab-test-booking'),
    path('lab-tests/add-to-cart/', enhanced_lab_views.add_test_to_cart, name='add-test-to-cart'),
    path('lab-tests/remove-from-cart/<int:cart_item_id>/', enhanced_lab_views.remove_test_from_cart, name='remove-test-from-cart'),
]