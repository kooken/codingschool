from django.db import models
from django.conf import settings

from users.models import ProgrammingLanguage, BonusModule


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
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField(null=True, blank=True)  # Ссылка на видео
    pdf_notes = models.FileField(upload_to='lesson_notes/', null=True, blank=True)  # Конспект в PDF
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


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


class Test(models.Model):
    lesson = models.OneToOneField(Lesson, related_name='test', on_delete=models.CASCADE)
    questions = models.JSONField()  # Сохранение вопросов и ответов в формате JSON

    def __str__(self):
        return f"Test for {self.lesson.title}"
