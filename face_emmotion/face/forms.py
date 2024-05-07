from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['fullname'].widget.attrs.update({'class': 'form-control'})
        self.fields['age'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control custom-select'})  # Add 'custom-select' for Bootstrap select
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['mobile'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control','rows': 3})

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'fullname', 'age', 'gender', 'email', 'mobile', 'address']

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
