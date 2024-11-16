# users/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, email_verification, ProfileView, UserPasswordResetView

# urlpatterns = [
#     path('register/', views.register, name='register'),  # Страница регистрации
#     path('login/', views.login_view, name='login'),  # Страница логина
#     path('profile/', views.profile, name='profile'),  # Страница профиля пользователя
# ]

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email_confirm/<str:token>/', email_verification, name='email_confirm'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('recovery_form/', UserPasswordResetView.as_view(), name='recovery_form'),
]
