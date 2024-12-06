from django.db import models
from django.conf import settings
from users.models import ProgrammingLanguage, BonusModule, User
from enum import Enum


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
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} (Course: {self.course.title})"

    def is_completed(self, user):
        test_result = LessonTestResult.objects.filter(user=user, test=self.test).order_by('-date_taken').first()
        homework_status = HomeworkSubmission.objects.filter(homework=self.homework, user=user).order_by(
            '-submitted_at').first()

        test_passed = test_result and test_result.is_passed()
        homework_done = homework_status and homework_status.status == 'approved'

        return test_passed and homework_done

    def unlock_next_lesson(user, current_lesson):
        if current_lesson.is_completed(user):
            next_lesson = Lesson.objects.filter(course=current_lesson.course, order__gt=current_lesson.order).first()
            if next_lesson:
                return next_lesson
        return None

    class Meta:
        ordering = ['order']


class LessonTest(models.Model):
    lesson = models.OneToOneField(Lesson, related_name="test", on_delete=models.CASCADE)
    min_score_required = models.IntegerField(default=50)

    def __str__(self):
        return f"Test for {self.lesson.title}"


class LessonTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(LessonTest, related_name="results", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f"Test result for {self.user.email} (Score: {self.score})"

    def is_passed(self):
        return self.score >= self.test.min_score_required

    def retake(self):
        if self.score < 100:
            self.attempts += 1
            self.score = 0
            self.save()
            return True
        return False


class LessonTestAnswer(models.Model):
    result = models.ForeignKey(LessonTestResult, related_name="answers", on_delete=models.CASCADE)
    question_id = models.IntegerField()
    answer_id = models.IntegerField()

    def __str__(self):
        return f"Answer ID: {self.answer_id} for question ID: {self.question_id}"


class Homework(models.Model):
    lesson = models.OneToOneField(Lesson, related_name="homework", on_delete=models.CASCADE)
    task_description = models.TextField()
    video_solution_url = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Homework for {self.lesson.title}"


class HomeworkSubmissionTypes(Enum):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REVISE = 'revise', 'Needs Revision'
    REJECTED = 'rejected', 'Rejected'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class HomeworkSubmissionStatuses(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_statuses(cls):
        for status in HomeworkSubmissionTypes:
            cls.objects.get_or_create(
                value=status.value[0],
                display_name=status.value[1]
            )


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, related_name="submissions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    github_link = models.URLField(max_length=200)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField()
    status = models.ForeignKey(
        HomeworkSubmissionStatuses,
        on_delete=models.CASCADE,
        related_name="submission_status",
        verbose_name="Submission Status",
        default=1
    )

    def __str__(self):
        return f"Submission by {self.user.email} (Status: {self.status})"


class LessonLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f"Liked by {self.user.email} on {self.lesson.title}"

    class Meta:
        unique_together = ('user', 'lesson')


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.lesson.title}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='bookmarks', on_delete=models.CASCADE)

    def __str__(self):
        return f"User {self.user.email} added bookmark on {self.lesson.title}"

    class Meta:
        unique_together = ('user', 'lesson')


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='feedback', on_delete=models.CASCADE)
    feedback_text = models.TextField()
    feedback_question_id = models.IntegerField()
    feedback_answer_id = models.IntegerField()

    def __str__(self):
        return f"Feedback by {self.user.email} on {self.lesson.title}"

    class Meta:
        unique_together = ('user', 'lesson')


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='report', on_delete=models.CASCADE)
    report_text = models.TextField()

    def __str__(self):
        return f"Report by {self.user.email} on {self.lesson.title}"

    class Meta:
        unique_together = ('user', 'lesson')
