from django import forms
from .models import Medicine
from .hsn_utils import auto_fetch_hsn_code, get_composition_suggestions

class MedicineForm(forms.ModelForm):
    # Add button for HSN auto-fetch
    fetch_hsn = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'fetch_hsn_checkbox'
        }),
        label='Auto-fetch HSN Code'
    )
    
    class Meta:
        model = Medicine
        fields = [
            'name', 'composition', 'hsn_code', 'weight', 'quantity', 'price', 
            'stock_quantity', 'Prescription_reqiuired', 'medicine_category', 
            'medicine_type', 'description', 'featured_image', 'expiry_date'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medicine name (e.g., Paracetamol 500mg)',
                'id': 'medicine_name'
            }),
            'composition': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter active ingredients and quantities (e.g., Paracetamol 500mg per tablet)',
                'id': 'medicine_composition'
            }),
            'hsn_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HSN Code (will be auto-filled)',
                'id': 'hsn_code_field',
                'readonly': False
            }),
            'weight': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg, 10ml, 1 tablet'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medicine_category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'medicine_category'
            }),
            'medicine_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'Prescription_reqiuired': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make featured_image optional
        self.fields['featured_image'].required = False
        self.fields['featured_image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        
        # Add help texts
        self.fields['composition'].help_text = 'Enter the active ingredients and their quantities. This helps in HSN code identification.'
        self.fields['hsn_code'].help_text = 'HSN (Harmonized System of Nomenclature) code for tax classification. Will be auto-filled based on medicine details.'
        
        # If editing existing medicine, try to fetch HSN if not present
        if self.instance.pk and not self.instance.hsn_code:
            self.auto_populate_hsn()
    
    def auto_populate_hsn(self):
        """Auto-populate HSN code based on medicine details"""
        if hasattr(self.instance, 'name') and self.instance.name:
            hsn_result = auto_fetch_hsn_code(
                medicine_name=self.instance.name,
                composition=getattr(self.instance, 'composition', None),
                category=getattr(self.instance, 'medicine_category', None)
            )
            
            if hsn_result.get('hsn_code'):
                self.fields['hsn_code'].initial = hsn_result['hsn_code']
                
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        composition = cleaned_data.get('composition')
        category = cleaned_data.get('medicine_category')
        fetch_hsn = cleaned_data.get('fetch_hsn', True)
        hsn_code = cleaned_data.get('hsn_code')
        
        # Auto-fetch HSN code if requested and not manually provided
        if fetch_hsn and name and not hsn_code:
            hsn_result = auto_fetch_hsn_code(
                medicine_name=name,
                composition=composition,
                category=category
            )
            
            if hsn_result.get('hsn_code'):
                cleaned_data['hsn_code'] = hsn_result['hsn_code']
                
                # Store additional info for display
                self._hsn_info = {
                    'source': hsn_result.get('source', 'unknown'),
                    'confidence': hsn_result.get('confidence', 'low'),
                    'suggestions': hsn_result.get('suggestions', [])
                }
        
        return cleaned_data
    
    def get_hsn_info(self):
        """Get HSN code fetch information for display"""
        return getattr(self, '_hsn_info', None)