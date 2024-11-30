from django.db import models
from django.conf import settings

from users.models import ProgrammingLanguage, BonusModule, User


class Course(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    programming_languages = models.ManyToManyField(ProgrammingLanguage, related_name='courses')
    bonus_modules = models.ManyToManyField(BonusModule, related_name='courses')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(max_length=200, null=True, blank=True)
    pdf_notes = models.FileField(upload_to='lesson_notes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey('Course', related_name='lessons', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()  # Порядок урока в курсе

    def __str__(self):
        return f"{self.title} (Course: {self.course.title})"

    def is_completed(self, user):
        """Проверка, выполнен ли урок пользователем."""
        test_result = LessonTestResult.objects.filter(user=user, test=self.test).order_by('-date_taken').first()
        homework_status = HomeworkSubmission.objects.filter(homework=self.homework, user=user).order_by(
            '-submitted_at').first()

        test_passed = test_result and test_result.is_passed()
        homework_done = homework_status and homework_status.status == 'approved'

        return test_passed and homework_done

    def unlock_next_lesson(user, current_lesson):
        """Открыть следующий урок после выполнения текущего."""
        if current_lesson.is_completed(user):
            next_lesson = Lesson.objects.filter(course=current_lesson.course, order__gt=current_lesson.order).first()
            if next_lesson:
                return next_lesson
        return None

    class Meta:
        ordering = ['order']


class LessonTest(models.Model):
    lesson = models.OneToOneField(Lesson, related_name="test", on_delete=models.CASCADE)
    min_score_required = models.IntegerField(default=50)  # Минимальный порог прохождения

    def __str__(self):
        return f"Test for {self.lesson.title}"


class LessonTestQuestion(models.Model):
    test = models.ForeignKey(LessonTest, related_name="questions", on_delete=models.CASCADE)
    question_text = models.TextField()
    answer_choices = models.JSONField()  # Варианты ответов
    correct_answer = models.CharField(max_length=255)  # Правильный ответ

    def __str__(self):
        return f"Question: {self.question_text}"


class LessonTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(LessonTest, related_name="results", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # Набранные баллы
    date_taken = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)  # Количество попыток

    def __str__(self):
        return f"Test result for {self.user.username} (Score: {self.score})"

    def is_passed(self):
        """Проверка, сдан ли тест."""
        return self.score >= self.test.min_score_required

    def retake(self):
        """Логика пересдачи теста."""
        if self.score < 100:  # Пересдача разрешена, если не набрано 100 баллов
            self.attempts += 1
            self.score = 0  # Обнулить баллы для пересдачи
            self.save()
            return True
        return False


class Homework(models.Model):
    lesson = models.OneToOneField(Lesson, related_name="homework", on_delete=models.CASCADE)
    task_description = models.TextField()
    video_solution_url = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Homework for {self.lesson.title}"


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, related_name="submissions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    github_link = models.URLField(max_length=200)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('revise', 'Needs Revision'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )

    def __str__(self):
        return f"Submission by {self.user.username} (Status: {self.status})"


class LessonLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'lesson')


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.lesson.title}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='bookmarks', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'lesson')
