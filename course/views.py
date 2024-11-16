# course/views.py
from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson


def course_list(request):
    return render(request, 'course/course_list.html')
    # courses = Course.objects.all()
    # return render(request, 'course/course_list.html', {'courses': courses})

    # def course_detail(request, course_id):


def course_detail(request):
    return render(request, 'course/course_detail.html')


# course = get_object_or_404(Course, id=course_id)
# return render(request, 'course/course_detail.html', {'course': course})


def course_by_category(request, category):
    courses = Course.objects.filter(category=category)
    return render(request, 'course/course_list.html', {'courses': courses, 'category': category})


def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    return render(request, 'course/lesson_detail.html', {'course': course, 'lesson': lesson})
