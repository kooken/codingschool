from django.utils import timezone
from enum import Enum
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
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
    FOREVER = 0, 'Forever'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class SubscriptionDurationTypes(models.Model):
    value = models.PositiveIntegerField(unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @property
    def duration_in_months(self):
        # Определяем количество месяцев для каждого типа подписки
        if self.value == 1:
            return 1
        elif self.value == 3:
            return 3
        elif self.value == 6:
            return 6
        elif self.value == 12:
            return 12
        elif self.value == 0:  # Для бессрочной подписки
            return None  # Возвращаем None, чтобы в коде можно было явно проверить это
        return None  # Если значение неизвестно, возвращаем None

    @classmethod
    def create_default_duration(cls):
        # Создаем записи для всех типов длительности подписки
        for duration in SubscriptionDurationType:
            cls.objects.get_or_create(
                value=duration.value[0],  # значение как строка
                display_name=duration.value[1]
            )


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


class SubscriptionPlanModes(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_sub_plans(cls):
        # Создаем записи для всех языков программирования из enum
        for subs in SubscriptionPlanType:
            cls.objects.get_or_create(
                value=subs.value[0],
                display_name=subs.value[1]
            )


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
    name = models.ForeignKey(
        SubscriptionPlanModes,
        on_delete=models.CASCADE,
        related_name="subscription_plans",
        verbose_name="Subscription Plan Mode"
    )
    duration = models.ForeignKey(
        SubscriptionDurationTypes,
        on_delete=models.CASCADE,
        related_name="subscription_plans",
        verbose_name="Subscription Duration"
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    programming_languages = models.ManyToManyField(
        ProgrammingLanguage,
        related_name='subscription_plans',
        blank=True
    )
    bonus_modules = models.ManyToManyField(
        BonusModule,
        related_name='subscription_plans',
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.duration}"


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="User"
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
        verbose_name="Subscription Plan"
    )
    programming_languages = models.ManyToManyField(ProgrammingLanguage, related_name="user_prog_subscriptions")
    bonus_modules = models.ManyToManyField(BonusModule, related_name="user_bonus_subscriptions")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateTimeField(null=True, blank=True)  # Добавьте null=True

    def save(self, *args, **kwargs):
        # Получаем текущее время с временной зоной
        now = timezone.now()

        # Если подписка бессрочная, устанавливаем end_date в None
        if self.plan.duration.duration_in_months == 0:
            self.end_date = None
        elif not self.end_date:  # Если end_date не задано, рассчитываем его
            if self.plan.duration.duration_in_months == 1:
                self.end_date = now + relativedelta(months=1)
            elif self.plan.duration.duration_in_months == 3:
                self.end_date = now + relativedelta(months=3)
            elif self.plan.duration.duration_in_months == 6:
                self.end_date = now + relativedelta(months=6)
            elif self.plan.duration.duration_in_months == 12:
                self.end_date = now + relativedelta(years=1)

        # Если end_date не равен None, проверяем, осведомлен ли он
        if self.end_date is not None and timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)  # Преобразуем наивную дату в осведомленную

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.start_date} - {self.end_date})"

    def __str__(self):
        return f"{self.user} - {self.plan.name} ({self.start_date} - {self.end_date})"

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
    is_active = models.BooleanField(default=True, verbose_name="Is Active")  # Промокод активен, пока не использован
    programming_languages = models.ManyToManyField(
        'ProgrammingLanguage',
        related_name="promo_codes",
        blank=True,
        verbose_name="Programming Languages"
    )
    bonus_modules = models.ManyToManyField(
        'BonusModule',
        related_name="promo_codes",
        blank=True,
        verbose_name="Bonus Modules"
    )

    def __str__(self):
        return self.code

    def is_valid(self):
        """Проверяет, активен ли промокод"""
        return self.is_active

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
