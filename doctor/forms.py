from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from hospital.models import User
from .models import Doctor_Information
# # Create a custom form that inherits from user form (reason --> for modify and customize)


class DoctorUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='Username can contain spaces (e.g., "Dr John Doe")',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username (spaces allowed, e.g., "Dr Smith")',
            'class': 'form-control floating'
        })
    )
    
    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(DoctorUserCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add styling to other fields
        self.fields['email'].widget.attrs.update({
            'placeholder': 'doctor@email.com',
            'class': 'form-control floating'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password (min 6 characters)',
            'class': 'form-control floating'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-control floating'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        # Allow multiple users with same email - removed uniqueness check
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Allow spaces and validate
        if not username:
            raise forms.ValidationError("Username is required.")
        
        # Allow spaces and most characters, but check length
        username_clean = username.strip()
        if len(username_clean) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 150:
            raise forms.ValidationError("Username cannot exceed 150 characters.")
        
        # Check for uniqueness (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(f"Username '{username}' is already taken. Please choose another one.")
        
        return username_clean  # Remove leading/trailing spaces but keep internal spaces

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        # Minimum 6 characters - allows username=password
        if password1 and len(password1) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password1
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2


class DoctorForm(ModelForm):
    class Meta:
        model = Doctor_Information
        fields = ['name', 'email', 'phone_number', 'degree', 'department',
                  'featured_image', 'visiting_hour', 'consultation_fee', 'report_fee', 'dob', 'hospital_name']

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
