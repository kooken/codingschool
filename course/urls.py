# course/urls.py
from django.urls import path
from . import views
from course.apps import CourseConfig

app_name = CourseConfig.name

urlpatterns = [
    path('course/', views.course_list, name='course_list'),  # Страница со списком курсов
    # path('<int:course_id>/', views.course_detail, name='course_detail'),  # Страница детального описания курса
    path('template/', views.course_detail, name='course_detail'),  # template
    path('category/<str:category>/', views.course_by_category, name='course_by_category'),  # Фильтрация курсов по категории
    path('<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),  # Страница с уроком курса
    # добавьте другие страницы, если нужно, например, для поиска, фильтрации и т.д.
]
