import json
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from users.models import User
from .forms import LessonTestForm, CommentForm, HomeworkSubmissionFormStudent, \
    HomeworkSubmissionFormAdmin
from .models import Course, Homework, LessonTestAnswer, Lesson, LessonTestResult, HomeworkSubmission, \
    HomeworkSubmissionStatuses
from urllib.parse import urlparse, parse_qs


def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    print("Course fetched:", course)
    course_name = course.title.lower().replace("course", "").strip()
    print("Course stripped name:", course_name)
    lessons = course.lessons.all().order_by('order')
    print("Lessons from course:", lessons)
    user = request.user
    print("Current user is:", user)

    lesson_data = []
    test_data = []
    for lesson in lessons:
        video_url = lesson.video_url
        embed_url = ''
        test_path = os.path.join(settings.MEDIA_ROOT,
                                 f'course/static/course/lesson_tests/{course_name}/{lesson.order}_lesson.json')
        print("Searching for test file in:", test_path)

        if os.path.exists(test_path):
            with open(test_path, 'r', encoding='utf-8') as file:
                test_data = json.load(file)

        notes_path = os.path.join(settings.MEDIA_ROOT,
                                  f'course/static/course/lesson_json_notes/{course_name}/{lesson.order}_lesson.json')
        print("Searching for notes file in:", notes_path)

        if os.path.exists(notes_path):
            with open(notes_path) as file:
                notes_data = json.load(file)

        if video_url:
            parsed_url = urlparse(video_url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]

            if video_id:
                embed_url = f"https://www.youtube.com/embed/{video_id}?si=OntB9hOa5AGwDJFT"

        test_result = LessonTestResult.objects.filter(user=request.user, test__lesson=lesson).first()
        total_questions = len(test_data) if test_data else 0
        homework_data = HomeworkSubmission.objects.filter(user=request.user, homework__lesson=lesson).first()
        is_completed = lesson.is_completed(user) if lesson.order != 1 else True
        print(f'Lesson {lesson.title} is completed? {is_completed}')

        lesson_data.append({'lesson': lesson, 'embed_url': embed_url, 'test_data': test_data,
                            'test_result': test_result, 'total_questions': total_questions,
                            'homework_data': homework_data, 'notes_data': notes_data, 'is_completed': is_completed})

    lesson_order = request.POST.get("lesson_order")
    if lesson_order:
        lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
    else:
        lesson = lessons.first()
    print("Current lesson:", lesson)

    if request.method == "POST":
        print("Request POST data:", request.POST)
        if "submit_comment" in request.POST:
            lesson_order = request.POST.get("lesson_order")
            print("Lesson order is:", lesson_order)
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            print("Fetched lesson is:", lesson)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.lesson = lesson
                comment.user = request.user
                comment.save()

        if "submit_test" in request.POST:
            lesson_order = request.POST.get("lesson_order")
            print("Lesson order is:", lesson_order)
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            print("Lesson is:", lesson)
            lesson_data_item = next((item for item in lesson_data if item['lesson'] == lesson), None)
            if lesson_data_item:
                current_test_data = lesson_data_item['test_data']
                print("Test data for lesson:", current_test_data)
            else:
                print("No lesson data found for this lesson")
            test_form = LessonTestForm(questions=current_test_data, data=request.POST)

            if test_form.is_valid():
                user_answers = [
                    test_form.cleaned_data[f'question_{i + 1}'] for i in range(len(current_test_data))
                ]
                print("User answers are:", user_answers)

                correct_answers = [q['correct_answer'] for q in current_test_data]
                print("Correct answers are:", correct_answers)

                score = sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
                print("Score is:", score)

                percentage = (score / len(correct_answers)) * 100 if correct_answers else 0
                print("Percentage is:", percentage)

                test_result, created = LessonTestResult.objects.get_or_create(
                    user=request.user, test=lesson.test
                )
                test_result.score = percentage
                test_result.attempts += 1
                test_result.save()
                print("Test result object is:", test_result)

                for i, user_answer in enumerate(user_answers):
                    question = current_test_data[i]
                    answer_id = question['answer_choices'].index(user_answer) + 1

                    LessonTestAnswer.objects.create(
                        result=test_result,
                        question_id=question['id'],
                        answer_id=answer_id
                    )

            if not test_form.is_valid():
                print("Form errors:", test_form.errors)

        if "retake_test" in request.POST:
            lesson_order = request.POST.get("lesson_order")
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            test_result = LessonTestResult.objects.filter(user=request.user, test__lesson=lesson).first()

            if test_result:
                test_result.answers.all().delete()

            reset_test = True

        if "submit_homework" in request.POST:
            lesson_order = request.POST.get("lesson_order")
            print("Lesson order is:", lesson_order)

            if lesson_order:
                lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
                print("Fetched lesson is:", lesson)

                try:
                    homework = lesson.homework
                    print("Homework for this lesson is:", homework)
                except Homework.DoesNotExist:
                    return JsonResponse({"message": "No homework is associated with this lesson."}, status=400)

                homework_form = HomeworkSubmissionFormStudent(request.POST)

                if homework_form.is_valid():
                    homework_submission = homework_form.save(commit=False)
                    homework_submission.homework = homework
                    homework_submission.user = request.user
                    homework_submission.save()

                else:
                    return JsonResponse({"message": "There was an error with your submission."}, status=400)

    lessons = course.lessons.all()
    return render(request, "course/course_detail.html", {
        "course": course,
        "lesson": lesson,
        "test_data": test_data if 'test_data' in locals() else None,
        "lesson_data": lesson_data,
        "lessons": lessons,
        "percentage": percentage if 'percentage' in locals() else None,
        "total_questions": len(test_data),
        "result": test_result if 'test_result' in locals() else None,
        "reset_test": reset_test if 'reset_test' in locals() else False,
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

    return render(request, 'course/admin_main.html', {
        'hw_count': pending_count,
        'users': users,
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
