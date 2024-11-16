# main/urls.py
from django.urls import path
from . import views
from main.apps import MainConfig

app_name = MainConfig.name

urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('mission/', views.mission, name='mission'),
    path('team/', views.team, name='team'),
]
