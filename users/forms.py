# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=35, required=False)
    avatar = forms.ImageField(required=False)
    city = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['email', 'phone', 'avatar', 'city', 'password1', 'password2']
