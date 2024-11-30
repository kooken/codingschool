from django.urls import path
from . import views
from course.apps import CourseConfig
from course.views import AvailableCourseView

app_name = CourseConfig.name

urlpatterns = [
    path('available/', AvailableCourseView.as_view(), name='available_course'),
    path('course/<int:id>/', views.course_detail, name='course_detail'),
    # path('lesson/<int:lesson_id>/test/', views.take_test, name='take_test'),
    # path('lesson/<int:lesson_id>/comments/', views.lesson_comments, name='lesson_comments'),
    # path('lesson/<int:lesson_id>/submit_homework/', views.submit_homework, name='submit_homework'),
]
