from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'weight', 'quantity', 'price', 'stock_quantity',
            'Prescription_reqiuired', 'medicine_category', 'medicine_type',
            'description', 'featured_image', 'expiry_date'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['featured_image'].required = False
        self.fields['featured_image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })