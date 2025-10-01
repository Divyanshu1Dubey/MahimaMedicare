from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from hospital.models import User, Hospital_Information, Patient
from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician, hospital_department, specialization

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['username'].help_text = 'Required'
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add placeholder text
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Admin username',
            'class': 'form-control'
        })
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
            

class LabWorkerCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(LabWorkerCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class PharmacistCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(PharmacistCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

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


class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'email', 'phone_number', 'address', 'blood_group', 'history', 'dob', 'nid', 'featured_image', 
                  'prescription_image', 'prescription_notes']

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address not found.")
        return email


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        # Simple and clear help text
        self.fields['username'].help_text = 'Required'
        self.fields['email'].help_text = 'Required - Enter valid email'
        self.fields['password1'].help_text = 'Minimum 6 characters'
        self.fields['password2'].help_text = 'Enter same password'
        
        # Add placeholder text
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'email@example.com',
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


class DoctorRegistrationForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=hospital_department.objects.none(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    specialization = forms.ModelChoiceField(
        queryset=specialization.objects.none(),
        empty_label="Select Specialization",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    certificate_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        hospital_id = kwargs.pop('hospital_id', None)
        super(DoctorRegistrationForm, self).__init__(*args, **kwargs)
        
        if hospital_id:
            hospital = Hospital_Information.objects.get(hospital_id=hospital_id)
            self.fields['department'].queryset = hospital_department.objects.filter(hospital=hospital)
            self.fields['specialization'].queryset = specialization.objects.filter(hospital=hospital)