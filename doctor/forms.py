from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from hospital.models import User
from .models import Doctor_Information
# # Create a custom form that inherits from user form (reason --> for modify and customize)


class DoctorUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(DoctorUserCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['username'].help_text = 'Required'
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add placeholder text
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control floating'
        })
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
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use another email or login.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username

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
