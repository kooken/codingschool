import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import LessonTestForm, HomeworkSubmissionForm, CommentForm
from .models import Course, Homework, LessonTestAnswer, Lesson, LessonTestResult
from urllib.parse import urlparse, parse_qs


def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    print("Course fetched:", course)
    course_name = course.title.lower().replace("course", "").strip()
    print("Course stripped name:", course_name)
    lessons = course.lessons.all().order_by('order')  # Sorting lessons by order if necessary
    print("Lessons from course:", lessons)

    # Generate embed URLs for each lesson
    lesson_data = []
    for lesson in lessons:
        video_url = lesson.video_url
        embed_url = ''
        test_path = os.path.join(settings.MEDIA_ROOT,
                                 f'course/static/course/lesson_tests/{course_name}/{lesson.order}_lesson.json')
        print("Searching for test file in:", test_path)

        test_data = []
        if os.path.exists(test_path):
            with open(test_path, 'r', encoding='utf-8') as file:
                test_data = json.load(file)

        # If the video URL exists and is a YouTube URL, extract the video ID and create embed URL
        if video_url:
            parsed_url = urlparse(video_url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]

            if video_id:
                embed_url = f"https://www.youtube.com/embed/{video_id}?si=OntB9hOa5AGwDJFT"

        lesson_data.append({'lesson': lesson, 'embed_url': embed_url, 'test_data': test_data})

    lesson_order = request.POST.get("lesson_order")
    if lesson_order:
        lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
    else:
        lesson = lessons.first()  # Если не передан lesson_order, берём первый урок
    print("Current lesson:", lesson)

    # Получаем результат теста для текущего урока
    test_result = LessonTestResult.objects.filter(user=request.user, test__lesson=lesson).first()
    print("Test result:", test_result)

    # Обрабатываем POST-запросы для каждой формы
    if request.method == "POST":
        print("Request POST data:", request.POST)
        if "submit_comment" in request.POST:
            # Обработка комментариев
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
            # Get the lesson ID from the POST data
            lesson_order = request.POST.get("lesson_order")
            print("Lesson order is:", lesson_order)
            lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
            print("Lesson is:", lesson)
            test_form = LessonTestForm(questions=test_data, data=request.POST)
            # print("Test form is:", test_form)

            if test_form.is_valid():
                # Получаем ответы пользователя
                user_answers = [
                    test_form.cleaned_data[f'question_{i + 1}'] for i in range(len(test_data))
                ]
                print("User answers are:", user_answers)

                # Получаем правильные ответы
                correct_answers = [q['correct_answer'] for q in test_data]
                print("Correct answers are:", correct_answers)

                # Считаем баллы
                score = sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
                print("Score is:", score)

                # Рассчитываем процент правильных ответов
                percentage = (score / len(correct_answers)) * 100 if correct_answers else 0
                print("Percentage is:", percentage)

                # Создаем или обновляем результат теста
                test_result, created = LessonTestResult.objects.get_or_create(
                    user=request.user, test=lesson.test
                )
                test_result.score = percentage
                test_result.attempts += 1
                test_result.save()
                print("Test result object is:", test_result)

                # Сохраняем ответы пользователя
                for i, user_answer in enumerate(user_answers):
                    question = test_data[i]  # Извлекаем вопрос из JSON
                    answer_id = question['answer_choices'].index(user_answer) + 1

                    # Сохраняем ответ в модели LessonTestAnswer
                    LessonTestAnswer.objects.create(
                        result=test_result,
                        question_id=question['id'],
                        answer_id=answer_id
                    )

            if not test_form.is_valid():
                print("Form errors:", test_form.errors)

        if "retake_test" in request.POST:
            # Получаем старый результат
            test_result = LessonTestResult.objects.filter(user=request.user, test__lesson=lesson).first()

            if test_result:
                # Удаляем старые ответы
                test_result.answers.all().delete()
                # test_result.delete()

            # Устанавливаем переменную для отображения новой формы теста
            reset_test = True

        if "submit_homework" in request.POST:
            # Extract lesson order from POST data
            lesson_order = request.POST.get("lesson_order")
            print("Lesson order is:", lesson_order)

            if lesson_order:
                # Fetch the lesson using the lesson order
                lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
                print("Fetched lesson is:", lesson)

                # Ensure that the lesson has an associated Homework
                try:
                    homework = lesson.homework
                except Homework.DoesNotExist:
                    return JsonResponse({"message": "No homework is associated with this lesson."}, status=400)

                # Create the form instance with POST data
                homework_form = HomeworkSubmissionForm(request.POST)

                if homework_form.is_valid():
                    # Save the homework submission without committing to the database yet
                    homework_submission = homework_form.save(commit=False)
                    homework_submission.homework = homework  # Link to the correct homework
                    homework_submission.user = request.user  # Link to the current user
                    homework_submission.save()  # Save the instance to the database

                    return JsonResponse({"message": "Homework submitted successfully!"})
                else:
                    # Handle invalid form submission (if needed)
                    return JsonResponse({"message": "There was an error with your submission."}, status=400)

    # Загрузка курса с уроками
    lessons = course.lessons.all()
    return render(request, "course/course_detail.html", {
        "course": course,
        "lesson": lesson,
        "test_data": test_data,
        "lesson_data": lesson_data,
        "lessons": lessons,
        "percentage": percentage if 'percentage' in locals() else None,  # Проверяем, если есть процент
        "total_questions": len(test_data),
        "result": test_result if 'test_result' in locals() else None,  # Проверяем, если есть результат
        "reset_test": reset_test if 'reset_test' in locals() else False,  # Показываем форму заново
        "comment_form": CommentForm(),
        "homework_form": HomeworkSubmissionForm(),
        "test_form": LessonTestForm(),
    })


#
# def lesson_detail(request, lesson_id):
#     lesson = get_object_or_404(Lesson, order=lesson_id)
#
#     # Загрузить вопросы теста из JSON
#     test_file_path = '/Users/mariasazhina/code/codingschool/media/course/static/course/lesson_tests/python/1_lesson.json'
#
#     # Проверка наличия файла
#     if not os.path.exists(test_file_path):
#         return JsonResponse({'error': f"Test file not found: {test_file_path}"}, status=404)
#
#     # Загрузка теста
#     with open(test_file_path, 'r') as file:
#         test_data = json.load(file)
#
#     test_form = LessonTestForm(test_data['questions'])
#     homework_form = HomeworkSubmissionForm()
#
#     # Секция комментариев
#     comments = Comment.objects.filter(lesson=lesson)
#
#     if request.method == "POST":
#         # Проверка теста
#         if 'submit_test' in request.POST:
#             test_form = LessonTestForm(test_data['questions'], request.POST)
#             if test_form.is_valid():
#                 user_answers = [test_form.cleaned_data[f'question_{i + 1}'] for i in range(len(test_data['questions']))]
#                 correct_answers = [q['correct_answer'] for q in test_data['questions']]
#                 score = sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
#                 percentage = (score / len(correct_answers)) * 100
#                 return JsonResponse({'score': score, 'percentage': percentage})
#
#         # Загрузка ссылки на домашнее задание
#         if 'submit_homework' in request.POST:
#             homework_form = HomeworkSubmissionForm(request.POST)
#             if homework_form.is_valid():
#                 github_link = homework_form.cleaned_data['github_link']
#                 # Логика сохранения ссылки (например, в HomeworkSubmission)
#                 return JsonResponse({'message': 'Homework submitted successfully!'})
#
#     return render(request, 'lesson_detail.html', {
#         'lesson': lesson,
#         'test_form': test_form,
#         'homework_form': homework_form,
#         'comments': comments,
#     })
#
#
# class LessonListView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, course_id):
#         lessons = Lesson.objects.filter(course_id=course_id).order_by('order')
#         serializer = LessonSerializer(lessons, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class LessonDetailView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, lesson_id):
#         lesson = get_object_or_404(Lesson, id=lesson_id)
#         serializer = LessonSerializer(lesson)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class LessonTestSubmitView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, lesson_id):
#         lesson = get_object_or_404(Lesson, id=lesson_id)
#         test = lesson.test
#         questions = test.questions.all()
#
#         # Получение ответов от пользователя
#         user_answers = request.data.get('answers', {})  # {'question_id': 'user_answer'}
#
#         # Проверка ответов
#         correct_count = 0
#         total_questions = questions.count()
#
#         for question in questions:
#             user_answer = user_answers.get(str(question.id))
#             if user_answer == question.correct_answer:
#                 correct_count += 1
#
#         # Подсчет баллов
#         score = (correct_count / total_questions) * 100
#
#         # Сохранение результата теста
#         test_result, created = LessonTestResult.objects.get_or_create(
#             user=request.user,
#             test=test,
#         )
#         test_result.score = score
#         test_result.attempts += 1
#         test_result.save()
#
#         return Response(
#             {
#                 "score": score,
#                 "is_passed": test_result.is_passed(),
#                 "attempts": test_result.attempts,
#             },
#             status=status.HTTP_200_OK,
#         )
#
#
# class HomeworkSubmitView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, lesson_id):
#         lesson = get_object_or_404(Lesson, id=lesson_id)
#         homework = lesson.homework
#
#         # Создание или обновление домашки
#         submission, created = HomeworkSubmission.objects.get_or_create(
#             user=request.user,
#             homework=homework,
#         )
#         submission.github_link = request.data.get('github_link')
#         submission.status = 'pending'
#         submission.submitted_at = timezone.now()
#         submission.save()
#
#         return Response(
#             {"message": "Homework submitted successfully.", "status": submission.status},
#             status=status.HTTP_200_OK,
#         )
#
#
# class NextLessonUnlockView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, lesson_id):
#         lesson = get_object_or_404(Lesson, id=lesson_id)
#
#         if not lesson.is_completed(request.user):
#             return Response(
#                 {"message": "Complete the current lesson to unlock the next one."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         next_lesson = Lesson.objects.filter(course=lesson.course, order__gt=lesson.order).first()
#         if next_lesson:
#             serializer = LessonSerializer(next_lesson)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         return Response({"message": "No more lessons in this course."}, status=status.HTTP_404_NOT_FOUND)
#
#
# class LessonTestRetakeView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, lesson_id):
#         lesson = get_object_or_404(Lesson, id=lesson_id)
#         test_result = LessonTestResult.objects.filter(user=request.user, test=lesson.test).first()
#
#         if not test_result:
#             return Response({"message": "You haven't taken this test yet."}, status=status.HTTP_400_BAD_REQUEST)
#
#         if test_result.score >= 100:
#             return Response({"message": "You already have the maximum score."}, status=status.HTTP_400_BAD_REQUEST)
#
#         test_result.retake()
#         return Response({"message": "Test reset for retake."}, status=status.HTTP_200_OK)
#
#
# class HomeworkReviewView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, submission_id):
#         submission = get_object_or_404(HomeworkSubmission, id=submission_id)
#
#         if not request.user.is_staff:
#             return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
#
#         status_choice = request.data.get("status")
#         if status_choice not in ['approved', 'revise', 'rejected']:
#             return Response({"message": "Invalid status choice."}, status=status.HTTP_400_BAD_REQUEST)
#
#         submission.status = status_choice
#         submission.reviewed_at = timezone.now()
#         submission.save()
#
#         return Response({"message": "Homework reviewed.", "status": submission.status}, status=status.HTTP_200_OK)
#
#
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

# def course_detail(request, id):
#     course = get_object_or_404(Course, id=id)
#     return render(request, 'course/course_detail.html', {'course': course})


# def take_test(request, lesson_id):
#     lesson = get_object_or_404(Lesson, order=lesson_id)
#     test_path = '/Users/mariasazhina/code/codingschool/media/course/static/course/lesson_tests/python/1_lesson.json'
#
#     if os.path.exists(test_path):
#         with open(test_path, 'r') as file:
#             test_data = json.load(file)
#     else:
#         return JsonResponse({'error': 'Test file not found'}, status=404)
#
#     if request.method == 'POST':
#         # Обработка ответов пользователя
#         user_answers = request.POST.getlist('answers')
#         # Логика проверки теста и подсчета баллов
#         pass
#
#     return render(request, 'course/test.html', {'test_data': test_data})


# def lesson_comments(request, lesson_id):
#     # Логика отображения комментариев
#     pass


# def submit_homework(request, lesson_id):
#     lesson = get_object_or_404(Lesson, id=lesson_id)
#     homework_form = HomeworkSubmissionForm()
#
#     if request.method == "POST":
#         homework_form = HomeworkSubmissionForm(request.POST)
#         if homework_form.is_valid():
#             github_link = homework_form.cleaned_data['github_link']
#             # Логика сохранения ссылки
#             return JsonResponse({'message': 'Homework submitted successfully!'})
#
#     return render(request, 'course/submit_homework.html', {
#         'lesson': lesson,
#         'homework_form': homework_form,
#     })

# def add_comment(request, lesson_id):
#     lesson = get_object_or_404(Lesson, id=lesson_id)
#     comment_form = CommentForm()
#
#     if request.method == "POST":
#         comment_form = CommentForm(request.POST)
#         if comment_form.is_valid():
#             comment = comment_form.save(commit=False)
#             comment.lesson = lesson
#             comment.user = request.user  # Предположим, что пользователь авторизован
#             comment.save()
#             return JsonResponse({'message': 'Comment added successfully!'})
#
#     return render(request, 'course/add_comment.html', {
#         'lesson': lesson,
#         'comment_form': comment_form,
#     })
