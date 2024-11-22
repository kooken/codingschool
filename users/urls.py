# users/urls.py
# from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import RegisterView, UserLoginView, email_verification, UserProfileView, CustomPasswordResetView, \
    CustomPasswordResetConfirmView, ChangePasswordView, \
    DeleteAccountView, user_logout
from django.contrib.auth import views as auth_views

# urlpatterns = [
#     path('register/', views.register, name='register'),  # Страница регистрации
#     path('login/', views.login_view, name='login'),  # Страница логина
#     path('profile/', views.profile, name='profile'),  # Страница профиля пользователя
# ]

app_name = UsersConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email_confirm/<str:token>/', email_verification, name='email_confirm'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    # Подтверждение, что письмо отправлено
    # path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    # Ввод нового пароля (по ссылке из письма)
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Завершение смены пароля
    # path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
