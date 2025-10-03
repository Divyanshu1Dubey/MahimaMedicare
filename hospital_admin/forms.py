from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from hospital.models import User, Hospital_Information
from .models import Admin_Information, Clinical_Laboratory_Technician

class AdminUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='Username can contain spaces (e.g., "Admin Name")',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username (spaces allowed, e.g., "Admin User")',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add styling to other fields
        self.fields['email'].widget.attrs.update({
            'placeholder': 'admin@hospital.com',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password (min 6 characters)',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-control'
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
            

class LabWorkerCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='Username can contain spaces (e.g., "Lab Worker")',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username (spaces allowed)',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(LabWorkerCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add styling to other fields
        self.fields['email'].widget.attrs.update({
            'placeholder': 'labworker@hospital.com',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password (min 6 characters)',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-control'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError("Username is required.")
        
        username_clean = username.strip()
        if len(username_clean) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 150:
            raise forms.ValidationError("Username cannot exceed 150 characters.")
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(f"Username '{username}' is already taken. Please choose another one.")
        
        return username_clean

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password1
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2

class PharmacistCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='Username can contain spaces (e.g., "Pharmacist Name")',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username (spaces allowed)',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(PharmacistCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add styling to other fields
        self.fields['email'].widget.attrs.update({
            'placeholder': 'pharmacist@hospital.com',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password (min 6 characters)',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-control'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError("Username is required.")
        
        username_clean = username.strip()
        if len(username_clean) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 150:
            raise forms.ValidationError("Username cannot exceed 150 characters.")
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(f"Username '{username}' is already taken. Please choose another one.")
        
        return username_clean

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password1
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2

# class EditLabWorkerForm(forms.ModelForm):
#     class Meta:
#         model = Clinical_Laboratory_Technician
#         fields = ['name', 'age', 'phone_number', 'featured_image']

#     def __init__(self, *args, **kwargs):
#         super(EditLabWorkerForm, self).__init__(*args, **kwargs)

#         for name, field in self.fields.items():
#             field.widget.attrs.update({'class': 'form-control'})



class AddHospitalForm(ModelForm):
    class Meta:
        model = Hospital_Information
        fields = ['name','address','featured_image','phone_number','email','hospital_type']

    def __init__(self, *args, **kwargs):
        super(AddHospitalForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class EditHospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital_Information
        fields = ['name','address','featured_image','phone_number','email','hospital_type']

    def __init__(self, *args, **kwargs):
        super(EditHospitalForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class EditEmergencyForm(forms.ModelForm):
    class Meta:
        model = Hospital_Information
        fields = ['general_bed_no','available_icu_no','regular_cabin_no','emergency_cabin_no','vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(EditEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class AddEmergencyForm(ModelForm):
    class Meta:
        model = Hospital_Information
        fields = ['name','general_bed_no','available_icu_no','regular_cabin_no','emergency_cabin_no','vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(AddEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})



class AdminForm(ModelForm):
    class Meta:
        model = Admin_Information
        fields = ['name', 'email', 'phone_number', 'role','featured_image']

    def __init__(self, *args, **kwargs):
         super(AdminForm, self).__init__(*args, **kwargs)

         for name, field in self.fields.items():
             field.widget.attrs.update({'class': 'form-control'})

