from datetime import timedelta

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

from config import settings
from users.managers import CustomUserManager


# Кастомный пользователь
class User(AbstractUser):
    # Дополнительные поля
    phone = models.CharField(max_length=35, verbose_name='Phone', null=True, blank=True)
    avatar = models.ImageField(upload_to='users/', verbose_name='Avatar', null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Country', null=True, blank=True)
    token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True)

    # Убираем стандартное поле username
    username = None

    # Указываем email как основное поле для аутентификации
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    subscription_plan = models.ForeignKey(
        'SubscriptionPlan', null=True, blank=True, on_delete=models.SET_NULL
    )
    subscription_start_date = models.DateTimeField(verbose_name='Subscription Start Date', null=True, blank=True)
    subscription_end_date = models.DateTimeField(verbose_name='Subscription End Date', null=True, blank=True)
    account_type = models.CharField(max_length=50, verbose_name='Account Type', null=True, blank=True)
    referral_code = models.CharField(max_length=100, verbose_name='Referral Code', null=True, blank=True)
    receive_newsletter = models.BooleanField(default=True, verbose_name='Receive Newsletter')
    receive_notifications = models.BooleanField(default=True, verbose_name='Receive Notifications')
    github_profile = models.CharField(max_length=255, verbose_name='Github', null=True, blank=True)
    linkedin_profile = models.CharField(max_length=255, verbose_name='LinkedIn', null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


# Модель подписки
class SubscriptionPlan(models.Model):
    EARLY_BIRD = 'early_bird'
    FREE = 'free'
    SINGLE_COURSE = 'single_course'
    TWO_COURSES = 'two_courses'
    THREE_COURSES = 'three_courses'
    FOUR_COURSES = 'four_courses'
    ALL_COURSES = 'all_courses'

    PLAN_CHOICES = [
        (EARLY_BIRD, 'Early Bird'),
        (FREE, 'Free'),
        (SINGLE_COURSE, '1 Course'),
        (TWO_COURSES, '2 Courses'),
        (THREE_COURSES, '3 Courses'),
        (FOUR_COURSES, '4 Courses'),
        (ALL_COURSES, 'All Courses'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Цена подписки
    benefits = models.JSONField(default=dict)  # Список преимуществ

    def __str__(self):
        return self.get_name_display()


SUBSCRIPTION_DURATIONS = [
    (1, '1 Month'),
    (3, '3 Months'),
    (6, '6 Months'),
    (12, '1 Year'),
]

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="User"
    )
    plan = models.ForeignKey(
        'SubscriptionPlan',
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Subscription Plan"
    )
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем дату окончания в зависимости от плана
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=30)  # Стандартно 1 месяц
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ['-start_date']
