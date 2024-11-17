import re

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from users.models import User
from django import forms


# class StyleFormMixin:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'
#
#
# class UserRegisterForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ('email', 'password1', 'password2')

class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'email' or field_name == 'username':
                field.widget.attrs['placeholder'] = 'Enter your email'
            elif field_name == 'password1' or field_name == 'password':
                field.widget.attrs['placeholder'] = 'Enter your password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Repeat your password'


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Изменение текста меток для каждого поля
        self.fields['email'].label = 'Your email address'
        self.fields['password1'].label = 'Create password'
        self.fields['password2'].label = 'Confirm password'

        self.fields['password1'].error_messages = {
            'required': 'Please enter a password.',
            'min_length': 'Your password must contain at least 8 characters.',
            'too_common': 'This password is too common. Please choose a more secure one.',
            'numeric': 'Password cannot be entirely numeric. Please include letters and symbols.'
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Проверяем первый пароль на валидность
        if len(password1) < 8:
            raise ValidationError('Your password must contain at least 8 characters.')

        # Проверяем, что пароль содержит буквы и цифры
        if not re.search(r'[A-Za-z]', password1) or not re.search(r'[0-9]', password1):
            raise ValidationError('Your password must include both letters and numbers.')

        # Проверяем, что пароль содержит специальные символы
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):  # \W включает любые неалфавитные символы
            raise ValidationError(
                'Your password must include at least one of the special characters (!@#$%^&*(),.?":{}|<>).')

        # Если первый пароль валидный, проверяем, совпадают ли оба пароля
        if password1 != password2:
            raise ValidationError('Please make sure your passwords match.')

        return password2

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Обновление меток для полей
        self.fields['username'].label = 'Your email address'
        self.fields['password'].label = 'Your password'

    def clean_email(self):
        email = self.cleaned_data.get('username')  # в AuthenticationForm по умолчанию используется 'username'
        password = self.cleaned_data.get('password')

        # Если email и пароль введены, то проверим их
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password. Please try again.")

        return self.cleaned_data['username']  # Возвращаем email (именно это поле используется для логина)

    class Meta:
        model = User
        fields = ('email', 'password',)


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()


# class UserRecoveryForm(StyleFormMixin, PasswordResetForm):
#     class Meta:
#         model = User
#         fields = ('email',)
