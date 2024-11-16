# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница логина
    path('profile/', views.profile, name='profile'),  # Страница профиля пользователя
]
