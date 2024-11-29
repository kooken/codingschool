from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Course, Lesson


class AvailableCourseView(LoginRequiredMixin, ListView):
    template_name = 'course/available_course.html'
    context_object_name = 'courses'

    def get_queryset(self):
        user = self.request.user

        if user.subscription_plan:
            programming_languages = user.subscription_plan.programming_languages.all()
            bonus_modules = user.subscription_plan.bonus_modules.all()

            courses_by_languages = Course.objects.filter(programming_languages__in=programming_languages)
            courses_by_modules = Course.objects.filter(bonus_modules__in=bonus_modules)

            courses = courses_by_languages | courses_by_modules
            courses = courses.distinct()

            return courses
        else:
            return Course.objects.none()


def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, 'course/course_detail.html', {'course': course})


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.filter(course__users=self.request.user)
