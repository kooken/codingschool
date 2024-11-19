import re

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, AuthenticationForm, \
    PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from users.models import User
from django import forms
from django.utils.translation import gettext_lazy as _  # Добавлен импорт


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

    def clean(self):
        email = self.cleaned_data.get('username')  # username используется как email
        password = self.cleaned_data.get('password')

        # Проверяем, что оба поля заполнены
        if not email or not password:
            raise ValidationError("Both email and password are required.")

        # Проверяем существование пользователя
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")

        # Пытаемся аутентифицировать пользователя
        user = authenticate(self.request, username=email, password=password)
        if user is None:
            raise ValidationError("Invalid email or password. Please try again.")

        # Проверяем, активен ли пользователь
        if not user.is_active:
            raise ValidationError("This account is inactive. Please contact support.")

        # Успешная валидация
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'phone', 'city', 'email']  # Поля для редактирования
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Изменение текста меток для каждого поля
        self.fields['new_password1'].label = _('Create new password')
        self.fields['new_password2'].label = _('Confirm new password')

        self.fields['new_password1'].error_messages = {
            'required': _('Please enter a password.'),
            'min_length': _('Your password must contain at least 8 characters.'),
            'too_common': _('This password is too common. Please choose a more secure one.'),
            'numeric': _('Password cannot be entirely numeric. Please include letters and symbols.')
        }
        self.fields.pop('old_password', None)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        # Проверка на длину пароля
        if len(password1) < 8:
            raise ValidationError(_('Your password must contain at least 8 characters.'))

        # Проверка на наличие букв и цифр
        if not re.search(r'[A-Za-z]', password1) or not re.search(r'[0-9]', password1):
            raise ValidationError(_('Your password must include both letters and numbers.'))

        # Проверка на наличие хотя бы одного специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError(_('Your password must include at least one special character (e.g., !@#$%^&*).'))

        # Проверка, совпадают ли пароли
        if password1 != password2:
            raise ValidationError(_('Please make sure your passwords match.'))

        return password2

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email address'
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Проверка на существование пользователя с таким email
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')

        return email
