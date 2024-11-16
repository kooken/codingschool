from django.contrib.auth.views import LoginView, PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from config.settings import EMAIL_HOST_USER
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
import secrets
from users.forms import UserRegisterForm, UserProfileForm, UserLoginForm, UserRecoveryForm
from users.models import User
import random, string


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('course:courses_list')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'
        send_mail(
            subject='Email confirmation',
            message=f'Hello! Click on the link to confirm your email: {url}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserLoginView(LoginView):
    model = User
    form_class = UserLoginForm
    # redirect_authenticated_user = True
    success_url = reverse_lazy('main:index')


class UserPasswordResetView(PasswordResetView):
    form_class = UserRecoveryForm
    template_name = 'users/recovery_form.html'

    def form_valid(self, form):
        user_email = self.request.POST.get('email')
        user = get_object_or_404(User, email=user_email)
        new_password = generate_random_password()
        user.set_password(new_password)
        user.save()
        send_mail(
            subject="Password recovery",
            message=f"Hey! Your password has been changed:\n"
                    f"Your new credentials:\n"
                    f"Email: {user_email}\n"
                    f"Password: {new_password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return redirect('users:login')
