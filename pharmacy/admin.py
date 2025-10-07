from django.contrib import admin

# Register your models here.
from .models import Medicine, Pharmacist, Cart, Order, PrescriptionUpload, PrescriptionMedicine

class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock_quantity', 'expiry_date', 'is_expiring_soon', 'price')
    list_filter = ('medicine_category','medicine_type')
    search_fields = ('name',)

class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 0
    fields = ['medicine', 'quantity', 'dosage', 'days', 'unit_price', 'total_price']
    readonly_fields = ['total_price']

class PrescriptionUploadAdmin(admin.ModelAdmin):
    list_display = ('upload_id', 'patient', 'status', 'pharmacist', 'uploaded_at', 'estimated_cost')
    list_filter = ('status', 'delivery_method', 'uploaded_at')
    search_fields = ('patient__name', 'doctor_name')
    readonly_fields = ('uploaded_at', 'reviewed_at', 'updated_at')
    inlines = [PrescriptionMedicineInline]

    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'prescription_image', 'doctor_name', 'prescription_date', 'patient_notes')
        }),
        ('Review & Processing', {
            'fields': ('status', 'pharmacist', 'pharmacist_notes', 'estimated_cost')
        }),
        ('Delivery Information', {
            'fields': ('delivery_method', 'delivery_address', 'delivery_phone')
        }),
        ('System Information', {
            'fields': ('related_order', 'uploaded_at', 'reviewed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Pharmacist)
admin.site.register(PrescriptionUpload, PrescriptionUploadAdmin)
admin.site.register(PrescriptionMedicine)
