# Payment Management Admin Configuration
from django.contrib import admin
from .models import PaymentRecord, PaymentVerificationLog, DailyPaymentSummary

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_type', 'payment_method', 'total_amount', 'status', 'is_admin_verified', 'created_at']
    list_filter = ['payment_type', 'payment_method', 'status', 'is_admin_verified', 'created_at']
    search_fields = ['payment_id', 'customer_name', 'customer_phone', 'razorpay_payment_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(PaymentVerificationLog)
class PaymentVerificationLogAdmin(admin.ModelAdmin):
    list_display = ['payment_record', 'admin_user', 'action_taken', 'previous_status', 'new_status', 'timestamp']
    list_filter = ['action_taken', 'previous_status', 'new_status', 'timestamp']
    search_fields = ['payment_record__payment_id', 'admin_user__username']
    readonly_fields = ['timestamp']

@admin.register(DailyPaymentSummary)
class DailyPaymentSummaryAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_payments', 'verified_payments', 'total_amount', 'verified_amount']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']