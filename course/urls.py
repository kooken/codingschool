from django.urls import path
from . import views
from course.apps import CourseConfig
from course.views import AvailableCourseView

app_name = CourseConfig.name

urlpatterns = [
    path('available/', AvailableCourseView.as_view(), name='available_course'),
    path('course/<int:id>/', views.course_detail, name='course_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
