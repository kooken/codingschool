from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect
from config.settings import EMAIL_HOST_USER
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
import secrets
from users.forms import UserRegisterForm, UserProfileForm, UserLoginForm
from users.models import User
import random, string
from django.template.loader import render_to_string


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('course:course_list')

    # def form_valid(self, form):
    #     user = form.save()
    #     user.is_active = False
    #     token = secrets.token_hex(16)
    #     user.token = token
    #     user.save()
    #     host = self.request.get_host()
    #     url = f'http://{host}/users/email_confirm/{token}/'
    #     send_mail(
    #         subject='Email confirmation',
    #         message=f'Hello! Click on the link to confirm your email: {url}',
    #         from_email=EMAIL_HOST_USER,
    #         recipient_list=[user.email]
    #     )
    #     return super().form_valid(form)
    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'

        # Рендерим HTML-шаблон
        html_message = render_to_string('emails/email_confirmation.html', {
            'email': user.email,
            'url': url,
        })

        # Текстовое письмо (резервный вариант)
        text_message = f'Hello! Click on the link to confirm your email: {url}'

        # Отправка письма с HTML и текстом
        email = EmailMultiAlternatives(
            subject='Email Confirmation',
            body=text_message,
            from_email=EMAIL_HOST_USER,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

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
    template_name = 'users/login.html'
    # redirect_authenticated_user = True
    success_url = reverse_lazy('course:course_list')


# class UserPasswordResetView(PasswordResetView):
#     form_class = UserRecoveryForm
#     template_name = 'users/recovery_form.html'
#
#     def form_valid(self, form):
#         user_email = self.request.POST.get('email')
#         user = get_object_or_404(User, email=user_email)
#         new_password = generate_random_password()
#         user.set_password(new_password)
#         user.save()
#         send_mail(
#             subject="Password recovery",
#             message=f"Hey! Your password has been changed:\n"
#                     f"Your new credentials:\n"
#                     f"Email: {user_email}\n"
#                     f"Password: {new_password}",
#             from_email=EMAIL_HOST_USER,
#             recipient_list=[user.email]
#         )
#         return redirect('users:login')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'emails/password_reset_email.html'  # Текстовое письмо (резервный вариант)
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        # Получаем email пользователя из формы
        email = form.cleaned_data["email"]
        user = get_object_or_404(User, email=email)

        # Генерируем токен сброса пароля
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())  # Убираем .decode()

        # Генерация ссылки для сброса пароля
        host = self.request.get_host()
        reset_url = f'http://{host}{reverse("users:password_reset_confirm", kwargs={"uidb64": uid, "token": token})}'

        # Рендерим HTML-шаблон для email
        html_message = render_to_string('emails/password_reset_email.html', {
            'email': user.email,
            'reset_url': reset_url,
        })

        # Текстовое письмо (резервный вариант)
        text_message = f'Hello! Click on the link to reset your password: {reset_url}'

        # Отправка письма с HTML и текстом
        email_message = EmailMultiAlternatives(
            subject="Password Reset Request",
            body=text_message,
            from_email=EMAIL_HOST_USER,
            to=[user.email],
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
