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
    
    # API endpoints for medicine management
    path('api/fetch-hsn/', api_views.fetch_hsn_code_ajax, name='fetch-hsn-ajax'),
    path('api/composition-suggestions/', api_views.get_composition_suggestions_ajax, name='composition-suggestions'),
    path('api/search-medicines/', api_views.search_existing_medicines, name='search-medicines-ajax'),
    
    # Old PayMongo URLs removed - now using Razorpay integration
]
    


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)