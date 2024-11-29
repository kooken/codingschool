from django.utils import timezone
from enum import Enum
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from config import settings
from users.managers import CustomUserManager


class Country(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone = models.CharField(max_length=35, verbose_name='Phone', null=True, blank=True)
    avatar = models.ImageField(upload_to='users/', verbose_name='Avatar', null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    country = models.ForeignKey('Country', related_name="users", null=True, blank=True, on_delete=models.SET_NULL)
    token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True)

    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    subscription_plan = models.ForeignKey(
        'SubscriptionPlan', null=True, blank=True, on_delete=models.SET_NULL, related_name='user_subscription_plan'
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
        if self.value == 1:
            return 1
        elif self.value == 3:
            return 3
        elif self.value == 6:
            return 6
        elif self.value == 12:
            return 12
        elif self.value == 0:
            return None
        return None

    @classmethod
    def create_default_duration(cls):
        for duration in SubscriptionDurationType:
            cls.objects.get_or_create(
                value=duration.value[0],
                display_name=duration.value[1]
            )


class SubscriptionPlanType(Enum):
    NEWBIE = 'newbie', 'Newbie'
    MIDDLE = 'middle', 'Middle'
    PRO = 'pro', 'Pro'

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
    DOCKER = 'docker', 'Docker'
    DJANGO = 'django', 'Django'
    HACKATHON = 'hackathon', 'Hackathon'
    CAREER = 'career', 'Career'
    CHALLENGE = 'challenge', 'Challenge'

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]


class ProgrammingLanguage(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_languages(cls):
        for language in ProgrammingLanguageType:
            cls.objects.get_or_create(
                value=language.value[0],
                display_name=language.value[1]
            )


class BonusModule(models.Model):
    value = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    @classmethod
    def create_default_modules(cls):
        for module in BonusModuleType:
            cls.objects.get_or_create(
                value=module.value[0],
                display_name=module.value[1]
            )


class SubscriptionPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_user",
        verbose_name="User"
    )
    is_active = models.BooleanField(default=False, verbose_name="Is Active")
    name = models.ForeignKey(
        SubscriptionPlanModes,
        on_delete=models.CASCADE,
        related_name="subscription_plan_name",
        verbose_name="Subscription Plan Name"
    )
    duration = models.ForeignKey(
        SubscriptionDurationTypes,
        on_delete=models.CASCADE,
        related_name="subscription_duration",
        verbose_name="Subscription Duration"
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    programming_languages = models.ManyToManyField(
        ProgrammingLanguage,
        related_name='subscription_prog_langs',
        blank=True,
    )
    bonus_modules = models.ManyToManyField(
        BonusModule,
        related_name='subscription_bonus_modules',
        blank=True
    )
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        now = timezone.now()

        if self.duration.duration_in_months == 0:
            self.end_date = None
        elif not self.end_date:
            if self.duration.duration_in_months == 1:
                self.end_date = now + relativedelta(months=1)
            elif self.duration.duration_in_months == 3:
                self.end_date = now + relativedelta(months=3)
            elif self.duration.duration_in_months == 6:
                self.end_date = now + relativedelta(months=6)
            elif self.duration.duration_in_months == 12:
                self.end_date = now + relativedelta(years=1)

        if self.end_date is not None and timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)

        super().save(*args, **kwargs)

    def __str__(self):
        programming_languages = ", ".join(
            [lang.display_name for lang in self.programming_languages.all()]
        )
        bonus_modules = ", ".join(
            [module.display_name for module in self.bonus_modules.all()]
        )
        return f"{self.name.display_name} - {self.duration.display_name}: {programming_languages}, {bonus_modules}"


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
        return self.is_active
