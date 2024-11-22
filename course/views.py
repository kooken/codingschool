# course/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Course, Lesson


class AvailableCourseView(LoginRequiredMixin, ListView):
    template_name = 'course/available_courses.html'
    context_object_name = 'course'

    def get_queryset(self):
        return self.request.user.course.all()


def course_detail(request):
    return render(request, 'course/course_detail.html')


# class CourseDetailView(LoginRequiredMixin, DetailView):
#     model = Course
#     template_name = 'courses/course_detail.html'
#     context_object_name = 'course'
#
#     def get_queryset(self):
#         return self.request.user.courses.all()


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.filter(course__users=self.request.user)


def course_list(request):
    return render(request, 'course/course_list.html')


# courses = Course.objects.all()
# return render(request, 'course/course_list.html', {'courses': courses})

# def course_detail(request, course_id):


# def course_detail(request):
#     return render(request, 'course/course_detail.html')


# course = get_object_or_404(Course, id=course_id)
# return render(request, 'course/course_detail.html', {'course': course})


def course_by_category(request, category):
    courses = Course.objects.filter(category=category)
    return render(request, 'course/course_list.html', {'courses': courses, 'category': category})

# def lesson_detail(request, course_id, lesson_id):
#     course = get_object_or_404(Course, id=course_id)
#     lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
#     return render(request, 'course/lesson_detail.html', {'course': course, 'lesson': lesson})
