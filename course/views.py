import json
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.views.generic import ListView
from config.settings import EMAIL_HOST_USER
from users.models import User
from .forms import LessonTestForm, CommentForm, HomeworkSubmissionFormStudent, \
    HomeworkSubmissionFormAdmin, ReportForm
from .models import Course, Lesson, LessonTestResult, HomeworkSubmission, \
    HomeworkSubmissionStatuses, Report
from urllib.parse import urlparse, parse_qs


def get_lesson_data(lesson, user, course_name):
    video_url = lesson.video_url
    embed_url = ''
    test_data, notes_data = None, None

    test_path = os.path.join(settings.MEDIA_ROOT,
                             f'course/static/course/lesson_tests/{course_name}/{lesson.order}_lesson.json')
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as file:
            test_data = json.load(file)

    notes_path = os.path.join(settings.MEDIA_ROOT,
                              f'course/static/course/lesson_json_notes/{course_name}/{lesson.order}_lesson.json')
    if os.path.exists(notes_path):
        with open(notes_path) as file:
            notes_data = json.load(file)

    if video_url:
        parsed_url = urlparse(video_url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]
        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}?si=OntB9hOa5AGwDJFT"

    is_completed = lesson.is_completed(user) if lesson.order != 1 else True

    if lesson.order == 1:
        is_open = True
    else:
        previous_lessons = lesson.course.lessons.filter(order__lt=lesson.order).order_by('order')
        is_open = all(prev_lesson.is_completed(user) for prev_lesson in previous_lessons)

    return {
        'lesson': lesson,
        'embed_url': embed_url,
        'test_data': test_data,
        'test_result': LessonTestResult.objects.filter(user=user, test__lesson=lesson).first(),
        'total_questions': len(test_data) if test_data else 0,
        'homework_data': HomeworkSubmission.objects.filter(user=user, homework__lesson=lesson).first(),
        'notes_data': notes_data,
        'is_completed': is_completed,
        'is_open': is_open,
    }


def handle_post_request(request, course, lesson_data):
    current_url = request.get_full_path()
    fragment = request.POST.get("fragment", "").strip() or "lesson1"
    lesson_order = request.POST.get("lesson_order")
    lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
    print("Current url is:", current_url)
    print("Current fragment is:", fragment)
    print("Current lesson is:", lesson)
    if "submit_comment" in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            lesson_order = request.POST.get("lesson_order")
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            comment = comment_form.save(commit=False)
            comment.lesson = lesson
            comment.user = request.user
            comment.save()
            return redirect(f"{request.path}#{fragment}")

    if "submit_report" in request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            lesson_order = request.POST.get("lesson_order")
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            report = report_form.save(commit=False)
            report.lesson = lesson
            report.user = request.user
            report.save()
            print("Redirect to:", redirect(f"{request.path}#{fragment}"))
            return redirect(f"{request.path}#{fragment}")
        else:
            print("Error during form render", report_form.errors)

    elif "submit_test" in request.POST:
        lesson_order = request.POST.get("lesson_order")
        lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
        lesson_data_item = next((item for item in lesson_data if item['lesson'] == lesson), None)
        if lesson_data_item:
            current_test_data = lesson_data_item['test_data']
        else:
            return None

        test_form = LessonTestForm(questions=current_test_data, data=request.POST)
        if test_form.is_valid():
            process_test_submission(request.user, lesson, test_form, current_test_data)

    elif "submit_homework" in request.POST:
        lesson_order = request.POST.get("lesson_order")
        lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
        homework_form = HomeworkSubmissionFormStudent(request.POST)
        if homework_form.is_valid():
            process_homework_submission(request.user, lesson, homework_form)
            return redirect(f"{request.path}#{fragment}")
        else:
            print("Homework form is invalid:", homework_form.errors)

    return render(request, "course/course_detail.html", {
        "course": course,
        "lesson": lesson,
        "lesson_data": lesson_data,
        "comment_form": CommentForm(),
        "homework_form": HomeworkSubmissionFormStudent(),
        "test_form": LessonTestForm(),
        "current_url": current_url,
        "fragment": fragment,
    })


def process_test_submission(user, lesson, test_form, current_test_data):
    user_answers = [
        test_form.cleaned_data[f'question_{i + 1}'] for i in range(len(current_test_data))
    ]
    correct_answers = [q['correct_answer'] for q in current_test_data]
    score = sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
    percentage = (score / len(correct_answers)) * 100 if correct_answers else 0

    test_result, created = LessonTestResult.objects.get_or_create(
        user=user, test=lesson.test
    )
    test_result.score = percentage
    test_result.attempts += 1
    test_result.save()


def process_homework_submission(user, lesson, homework_form):
    homework_submission = homework_form.save(commit=False)
    homework_submission.homework = lesson.homework
    homework_submission.user = user
    homework_submission.save()


def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    course_name = course.title.lower().replace("course", "").strip()
    user = request.user

    lessons = course.lessons.all().order_by('order')
    lesson_data = [get_lesson_data(lesson, user, course_name) for lesson in lessons]

    lesson_order = request.POST.get("lesson_order")
    lesson = get_object_or_404(Lesson, course=course, order=lesson_order) if lesson_order else lessons.first()

    if request.method == "POST":
        handle_post_request(request, course, lesson_data)

    return render(request, "course/course_detail.html", {
        "course": course,
        "lesson": lesson,
        "lesson_data": lesson_data,
        "comment_form": CommentForm(),
        "homework_form": HomeworkSubmissionFormStudent(),
        "test_form": LessonTestForm(),
    })


def is_admin_or_teacher(user):
    return user.is_superuser or user.groups.filter(name='teachers').exists()


@user_passes_test(is_admin_or_teacher)
def admin_dashboard(request):
    hw_submissions = HomeworkSubmission.objects.select_related('homework', 'user', 'status').order_by('-submitted_at')
    return render(request, 'course/admin_dashboard.html', {
        'hw_submissions': hw_submissions,
    })


@user_passes_test(is_admin_or_teacher)
def admin_main(request):
    pending_status = HomeworkSubmissionStatuses.objects.get(value='pending')
    pending_count = HomeworkSubmission.objects.filter(status=pending_status).count()
    users = User.objects.select_related('subscription_plan').prefetch_related(
        'subscription_plan__programming_languages',
        'subscription_plan__bonus_modules'
    )
    reports = Report.objects.all()

    return render(request, 'course/admin_main.html', {
        'hw_count': pending_count,
        'users': users,
        'reports': reports,
    })


@user_passes_test(is_admin_or_teacher)
def admin_homework_detail(request, id):
    print(f"Accessing admin_homework_detail view with ID: {id}")

    hw_submissions = HomeworkSubmission.objects.select_related('homework', 'user', 'status') \
        .filter(id=id) \
        .order_by('-submitted_at')
    print(f"Homework submissions fetched: {list(hw_submissions)}")

    users = User.objects.select_related('subscription_plan').prefetch_related(
        'subscription_plan__programming_languages',
        'subscription_plan__bonus_modules'
    )
    print(f"Users fetched: {users.count()}")

    if request.method == 'POST':
        print("POST request received.")
        form = HomeworkSubmissionFormAdmin(request.POST)
        if form.is_valid():
            print(f"Form is valid. Data: {form.cleaned_data}")

            hw_submission = hw_submissions.first()
            if hw_submission:
                hw_submission.status = form.cleaned_data['status']
                hw_submission.comment = form.cleaned_data['comment']
                hw_submission.reviewed_at = form.cleaned_data.get('reviewed_at', None)
                hw_submission.save()
                print(f"Updated homework submission: {hw_submission}")
            else:
                print("No homework submission found to update.")

        else:
            print(f"Form is invalid. Errors: {form.errors}")
            messages.error(request, 'Failed to update submission.')
    else:
        print("GET request received.")
        form = HomeworkSubmissionFormAdmin()

    return render(request, 'course/admin_homework_detail.html', {
        'hw_submissions': hw_submissions,
        'form': form,
        'users': users,
    })


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


def send_homework_email():
    pending_homeworks = HomeworkSubmission.objects.filter(status_id=1)
    staff_users = User.objects.filter(is_staff=True)

    for homework in pending_homeworks:
        homework_url = f"http://127.0.0.1:8000/course/homework/{homework.id}/"

        html_message = render_to_string('emails/homework_submission.html', {
            'homework_url': homework_url,
        })
        text_message = (
            f'Hello! You got a new homework to check!\n'
            f'Check it here: {homework_url}'
        )

        for user in staff_users:
            email = EmailMultiAlternatives(
                subject='New homework to check',
                body=text_message,
                from_email=EMAIL_HOST_USER,
                to=[user.email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
