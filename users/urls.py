# users/urls.py
# from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import RegisterView, UserLoginView, email_verification, ProfileView, CustomPasswordResetView, \
    CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views

# urlpatterns = [
#     path('register/', views.register, name='register'),  # Страница регистрации
#     path('login/', views.login_view, name='login'),  # Страница логина
#     path('profile/', views.profile, name='profile'),  # Страница профиля пользователя
# ]

app_name = UsersConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email_confirm/<str:token>/', email_verification, name='email_confirm'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]
