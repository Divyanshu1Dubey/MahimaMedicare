from django.contrib import admin

# Register your models here.
from .models import Medicine, Pharmacist
from .models import Cart, Order
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock_quantity', 'expiry_date', 'is_expiring_soon', 'price')
    list_filter = ('medicine_category','medicine_type')
    search_fields = ('name',)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Medicine)
admin.site.register(Pharmacist)
