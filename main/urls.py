# main/urls.py
from django.urls import path
from main import views
from main.apps import MainConfig
from main.views import promo_code_page

app_name = MainConfig.name

urlpatterns = [
    path('promo-code/', promo_code_page, name='promo_code_page'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('mission/', views.mission, name='mission'),
    path('team/', views.team, name='team'),
    path('community/', views.community, name='community'),
    path('job_search/', views.job_search, name='job_search'),
]
