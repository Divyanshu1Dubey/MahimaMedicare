from django.urls import path
from . import views

app_name = 'payment_management'

urlpatterns = [
    # Main dashboard
    path('', views.payment_dashboard, name='dashboard'),
    
    # Payment details and verification
    path('payment/<str:payment_id>/', views.payment_detail, name='payment_detail'),
    path('verify/<str:payment_id>/', views.verify_payment, name='verify_payment'),
    
    # Bulk operations
    path('bulk-verify/', views.bulk_verify_payments, name='bulk_verify'),
    
    # Reports and analytics
    path('reports/', views.payment_reports, name='payment_reports'),
    path('export/', views.export_payments, name='export_payments'),
]