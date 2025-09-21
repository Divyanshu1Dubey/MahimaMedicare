from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', views.admin_login, name='admin-login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/',views.admin_dashboard, name='admin-dashboard'),
    path('hospital-admin-profile/<int:pk>/', views.hospital_admin_profile,name='hospital-admin-profile'),
    path('appointment-list',views.appointment_list, name='appointment-list'),
    path('register-doctor-list/', views.register_doctor_list,name='register-doctor-list'),
    path('pending-doctor-list/', views.pending_doctor_list,name='pending-doctor-list'),
    path('forgot-password/', views.admin_forgot_password,name='admin_forgot_password'),
    path('hospital-list/', views.hospital_list,name='hospital-list'),
    path('add-hospital/', views.add_hospital,name='add-hospital'),
    path('edit-hospital/<int:pk>/', views.edit_hospital,name='edit-hospital'),
    path('delete-hospital/<int:pk>/', views.delete_hospital,name='delete-hospital'),
    path('hospital-list/', views.hospital_list,name='hospital-list'),
    path('add-pharmacist/', views.add_pharmacist,name='add-pharmacist'),
    #path('edit-hospital/', views.edit_hospital,name='edit-hospital'),
    path('invoice/',views.invoice, name='invoice'),
    path('invoice-report/',views.invoice_report, name='invoice_report'),
    path('lock-screen/', views.lock_screen,name='lock_screen'),
    path('login/',views.admin_login,name='admin_login'),
    path('patient-list/',views.patient_list, name='patient-list'),
    # path('register/', views.register,name='register'),
    path('admin_register/',views.admin_register,name='admin_register'),
    path('transactions-list/',views.transactions_list, name='transactions_list'),
    path('admin-logout/', views.logoutAdmin, name='admin-logout'),
    path('emergency/', views.emergency_details,name='emergency'),
    path('edit-emergency-information/<int:pk>/', views.edit_emergency_information,name='edit-emergency-information'),
    path('hospital-profile/', views.hospital_profile ,name='hospital-profile'),
    path('hospital-admin-profile/<int:pk>/', views.hospital_admin_profile,name='hospital-admin-profile'),
    path('create-invoice/<int:pk>/', views.create_invoice,name='create-invoice'),
    path('create-report/<int:pk>/', views.create_report,name='create-report'),
    path('add-lab-worker/', views.add_lab_worker,name='add-lab-worker'),
    path('lab-worker-list/', views.view_lab_worker,name='lab-worker-list'),
    path('edit-lab-worker/<int:pk>/', views.edit_lab_worker,name='edit-lab-worker'),
    path('medicine-list/', views.medicine_list,name='medicine-list'),
    path('add-medicine/', views.add_medicine,name='add-medicine'),
    path('edit-medicine/<int:pk>/', views.edit_medicine,name='edit-medicine'),
    path('delete-medicine/<int:pk>/', views.delete_medicine,name='delete-medicine'),
    path('department-image-list/<int:pk>', views.department_image_list,name='department-image-list'),
    path('admin-doctor-profile/<int:pk>/', views.admin_doctor_profile,name='admin-doctor-profile'),
    path('accept-doctor/<int:pk>/', views.accept_doctor,name='accept-doctor'),
    path('reject-doctor/<int:pk>/', views.reject_doctor,name='reject-doctor'),
    path('delete-department/<int:pk>',views.delete_department,name='delete-department'),
    path('edit-department/<int:pk>',views.edit_department,name='edit-department'),
    path('delete-specialization/<int:pk>/<int:pk2>/',views.delete_specialization,name='delete-specialization'),
    path('delete-service/<int:pk>/<int:pk2>/',views.delete_service,name='delete-service'),
    path('labworker-dashboard/', views.labworker_dashboard,name='labworker-dashboard'),
    path('pharmacist-list/', views.view_pharmacist,name='pharmacist-list'),
    path('edit-pharmacist/<int:pk>/', views.edit_pharmacist,name='edit-pharmacist'),
    path('mypatient-list/', views.mypatient_list,name='mypatient-list'),
    path('prescription-list/<int:pk>', views.prescription_list,name='prescription-list'),
    path('add-test/', views.add_test,name='add-test'),
    path('test-list/', views.test_list,name='test-list'),
    path('delete-test/<int:pk>/', views.delete_test,name='delete-test'),
    path('pharmacist-dashboard/', views.pharmacist_dashboard,name='pharmacist-dashboard'),
    path('pharmacist-sales/', views.pharmacist_sales, name='pharmacist-sales'),
    path('pharmacist-purchase-history/', views.pharmacist_purchase_history, name='pharmacist-purchase-history'),
    path('bulk-medicine-management/', views.bulk_medicine_management, name='bulk-medicine-management'),
    path('medicine/<int:pk>/increase/', views.increase_medicine_stock, name='increase-medicine-stock'),
    path('medicine/<int:pk>/decrease/', views.decrease_medicine_stock, name='decrease-medicine-stock'),
    path('report-history/', views.report_history,name='report-history'),
    path('upload-report-pdf/<int:report_id>/', views.upload_report_pdf, name='upload-report-pdf'),
    path('download-report-pdf/<int:report_id>/', views.download_report_pdf, name='download-report-pdf'),
    path('direct-upload-pdf-report/<int:patient_id>/', views.direct_upload_pdf_report, name='direct-upload-pdf-report'),
    path('specimen-count-data/', views.specimen_count_data, name='specimen-count-data'),
    
    # Enhanced Lab Management URLs
    path('lab-dashboard/', views.lab_dashboard, name='lab-dashboard'),
    path('lab-report-queue/', views.lab_report_queue, name='lab-report-queue'),
    path('assign-report-to-me/<int:report_id>/', views.assign_report_to_me, name='assign-report-to-me'),
    path('update-report-status/<int:report_id>/', views.update_report_status, name='update-report-status'),
    path('my-assigned-reports/', views.my_assigned_reports, name='my-assigned-reports'),
    path('report-detail-view/<int:report_id>/', views.report_detail_view, name='report-detail-view'),
    path('bulk-report-actions/', views.bulk_report_actions, name='bulk-report-actions'),
    
]
  


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
