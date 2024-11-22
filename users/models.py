from datetime import timedelta, timezone
from enum import Enum

from django.core.exceptions import ValidationError
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


class SubscriptionDurationType(Enum):
    ONE_MONTH = 1, '1 Month'
    THREE_MONTHS = 3, '3 Months'
    SIX_MONTHS = 6, '6 Months'
    ONE_YEAR = 12, '1 Year'
    FOREVER = None, 'Forever'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class SubscriptionPlanType(Enum):
    EARLY_BIRD = 'early_bird', 'Early Bird'
    FREE = 'free', 'Free'
    SINGLE_COURSE = 'single_course', '1 Course'
    TWO_COURSES = 'two_courses', '2 Courses'
    THREE_COURSES = 'three_courses', '3 Courses'
    FOUR_COURSES = 'four_courses', '4 Courses'
    ALL_COURSES = 'all_courses', 'All Courses'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class ProgrammingLanguageType(Enum):
    PYTHON = 'python', 'Python'
    JAVASCRIPT = 'javascript', 'JavaScript'
    C_LANG = 'c_lang', 'C'
    SQL = 'sql', 'SQL'
    GO_LANG = 'go_lang', 'GoLang'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class BonusModuleType(Enum):
    LINKED_IN = 'linkedin', 'LinkedIn'
    GITHUB = 'github', 'GitHub'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


# Модель для языков программирования
class ProgrammingLanguage(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_languages(cls):
        # Создаем записи для всех языков программирования из enum
        for language in ProgrammingLanguageType:
            cls.objects.get_or_create(
                value=language.value[0],
                display_name=language.value[1]
            )


# Модель для бонусных модулей
class BonusModule(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_modules(cls):
        # Создаем записи для всех бонусных модулей из enum
        for module in BonusModuleType:
            cls.objects.get_or_create(
                value=module.value[0],
                display_name=module.value[1]
            )


# Модель подписки
class SubscriptionPlan(models.Model):
    # Использование Enum для поля выбора
    name = models.CharField(max_length=50, choices=SubscriptionPlanType.choices(), unique=True)
    duration = models.CharField(max_length=50, choices=SubscriptionDurationType.choices(), unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    programming_languages = models.ManyToManyField(ProgrammingLanguage, related_name='subscription_plans', blank=True)
    bonus_modules = models.ManyToManyField(BonusModule, related_name='subscription_plans', blank=True)

    def __str__(self):
        return self.get_name_display()


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="User"
    )
    plan = models.ForeignKey(
        SubscriptionPlan,  # Привязка к одному плану подписки
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
        verbose_name="Subscription Plan"
    )
    duration = models.IntegerField(
        choices=SubscriptionDurationType.choices(),
        default=SubscriptionDurationType.ONE_MONTH.value[0],
        verbose_name="Subscription Duration"
    )
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем дату окончания в зависимости от длительности подписки
        if not self.end_date:
            if self.duration == SubscriptionDurationType.ONE_MONTH.value[0]:
                self.end_date = self.start_date + timedelta(days=30)
            elif self.duration == SubscriptionDurationType.THREE_MONTHS.value[0]:
                self.end_date = self.start_date + timedelta(days=90)
            elif self.duration == SubscriptionDurationType.SIX_MONTHS.value[0]:
                self.end_date = self.start_date + timedelta(days=180)
            elif self.duration == SubscriptionDurationType.ONE_YEAR.value[0]:
                self.end_date = self.start_date + timedelta(days=365)
            elif self.duration == SubscriptionDurationType.FOREVER.value[0]:
                self.end_date = None  # Навсегда

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"
        ordering = ['-start_date']


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Promo Code")
    plan = models.ForeignKey(
        'SubscriptionPlan',
        on_delete=models.CASCADE,
        related_name="promo_codes",
        verbose_name="Subscription Plan"
    )
    duration = models.IntegerField(
        choices=SubscriptionDurationType.choices(),
        verbose_name="Duration (Months)",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")  # Флаг для одноразового использования

    def __str__(self):
        return self.code

    def is_valid(self):
        """Проверяет, действителен ли промокод"""
        # Промокод активен и еще не использован
        return self.is_active and not self.is_used

    def activate(self, user):
        """Активирует промокод, создавая подписку для пользователя"""
        if not self.is_valid():
            raise ValidationError("Promo code is not valid or already used.")

        # Создаем подписку для пользователя
        subscription = UserSubscription(
            user=user,
            plan=self.plan,
            duration=self.duration,
            start_date=timezone.now(),  # начальная дата подписки
        )

        # Применяем языки программирования и бонусные модули из плана подписки
        subscription.programming_languages.set(self.plan.programming_languages.all())
        subscription.bonus_modules.set(self.plan.bonus_modules.all())

        # Сохраняем подписку
        subscription.save()

        # Устанавливаем промокод как использованный
        self.is_used = True
        self.save()

        return subscription

# class BonusModule(models.Model):
#     name = models.CharField(max_length=100, choices=BonusModuleType.choices(), unique=True)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.name

# class ProgrammingLanguage(models.Model):
#     name = models.CharField(max_length=100, choices=ProgrammingLanguageType.choices(), unique=True)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.name
