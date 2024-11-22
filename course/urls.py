# course/urls.py
from django.urls import path
from . import views
from course.apps import CourseConfig
from course.views import AvailableCourseView
# from course.views import CourseDetailView, LessonDetailView

app_name = CourseConfig.name

urlpatterns = [
    path('course_template/', views.course_list, name='course_list'),  # Страница со списком курсов
    path('available/', AvailableCourseView.as_view(), name='available_course'),
    # path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    # path('<int:course_id>/lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    # path('<int:course_id>/', views.course_detail, name='course_detail'),  # Страница детального описания курса
    path('course_detail_template/', views.course_detail, name='course_detail'),  # template
    # path('category/<str:category>/', views.course_by_category, name='course_by_category'),
    # Фильтрация курсов по категории
    # path('<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    # Страница с уроком курса
    # добавьте другие страницы, если нужно, например, для поиска, фильтрации и т.д.
]
