from django.contrib.auth.views import (LoginView, PasswordResetConfirmView,
                                       PasswordResetView, PasswordResetCompleteView, PasswordResetDoneView)
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from config.settings import EMAIL_HOST_USER
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, TemplateView
import secrets
from users.forms import UserRegisterForm, UserProfileForm, UserLoginForm, CustomPasswordResetForm, \
    CustomPasswordChangeForm, DeleteAccountForm, CustomPasswordUpdateForm
from users.models import User
from django.template.loader import render_to_string


def user_logout(request):
    logout(request)  # Завершаем сессию пользователя
    return redirect('main:index')  # Перенаправляем на главную страницу или страницу входа


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('course:course_list')

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


# class ProfileView(UpdateView):
#     model = User
#     form_class = UserProfileForm
#     success_url = reverse_lazy('users:profile')
#
#     def get_object(self, queryset=None):
#         return self.request.user


class UserLoginView(LoginView):
    model = User
    form_class = UserLoginForm
    template_name = 'users/login.html'
    # redirect_authenticated_user = True
    success_url = reverse_lazy('course:course_list')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'emails/password_reset_email.html'
    form_class = CustomPasswordResetForm  # Используем кастомную форму для проверки email
    # success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        # Получаем email пользователя
        email = form.cleaned_data["email"]
        user = get_object_or_404(User, email=email)

        # Генерируем токен для сброса пароля
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Генерация ссылки для сброса пароля
        host = self.request.get_host()
        reset_url = f'http://{host}{reverse_lazy("users:password_reset_confirm", kwargs={"uidb64": uid, "token": token})}'

        # Рендерим HTML-шаблон для email
        html_message = render_to_string('emails/password_reset_email.html', {
            'email': user.email,
            'reset_url': reset_url,
        })

        # Текстовое письмо (резервный вариант)
        text_message = f'Hello! Click on the link to reset your password: {reset_url}'

        # Отправляем email
        email_message = EmailMultiAlternatives(
            subject="Password Reset Request",
            body=text_message,
            from_email=EMAIL_HOST_USER,  # Замените на вашу почту
            to=[user.email],
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

        messages.success(self.request,
                         'A password reset link has been sent to your email address. Please check your inbox :)')

        return render(self.request, self.template_name, {'form': form})

    def form_invalid(self, form):
        # Очищаем сообщения, чтобы не показывались сообщения от предыдущих запросов
        storage = messages.get_messages(self.request)
        storage.used = True
        return super().form_invalid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomPasswordChangeForm  # Используем кастомную форму
    success_url = reverse_lazy('users:password_reset_complete')  # URL для перенаправления после успешной смены пароля

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Получаем uidb64 и token из URL параметров
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        # Добавляем их в контекст
        context['uidb64'] = uidb64
        context['token'] = token
        return context


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class UserProfileView(LoginRequiredMixin, FormView):
    template_name = 'users/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/change_password.html'
    form_class = CustomPasswordUpdateForm
    success_url = reverse_lazy('users:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)  # Чтобы пользователь не был разлогинен
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = 'users/delete_account.html'
    form_class = DeleteAccountForm
    success_url = reverse_lazy('main:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.request.user.delete()
        messages.success(self.request, 'Your account has been deleted.')
        return super().form_valid(form)
