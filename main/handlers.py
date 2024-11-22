from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from users.models import PromoCode, User, UserSubscription
from course.models import Course


class PromoCodeHandler:
    """Класс для обработки промокодов"""

    def __init__(self, user: User, promo_code: str):
        self.user = user
        self.promo_code = promo_code
        self.promo = None

    def validate_promo_code(self):
        """Проверяет валидность промокода"""
        try:
            self.promo = PromoCode.objects.get(code=self.promo_code, is_active=True)
        except PromoCode.DoesNotExist:
            raise ValidationError("Invalid or expired promo code.")

        # Проверяем количество оставшихся использований
        if self.promo.uses >= self.promo.max_uses:
            raise ValidationError("Promo code has reached its usage limit.")

    def activate_subscription(self):
        """Активирует подписку для пользователя"""
        if not self.promo:
            raise ValidationError("Promo code has not been validated.")

        # Устанавливаем дату окончания подписки
        start_date = now()
        end_date = start_date + timedelta(days=30 * self.promo.duration)

        # Создаем или обновляем подписку пользователя
        subscription, created = UserSubscription.objects.update_or_create(
            user=self.user,
            plan=self.promo.plan,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
            }
        )

        # Увеличиваем счетчик использования промокода
        self.promo.uses += 1
        self.promo.save()

        return subscription

    def grant_course_access(self):
        """Предоставляет доступ к курсам в зависимости от плана подписки"""
        if not self.promo:
            raise ValidationError("Promo code has not been validated.")

        # Получаем доступные курсы для выбранного плана
        available_courses = Course.objects.all()[:self.promo.plan.max_courses]

        # Связываем пользователя с курсами
        self.user.courses.add(*available_courses)

    def process(self):
        """Основной метод для обработки промокода"""
        self.validate_promo_code()
        subscription = self.activate_subscription()
        self.grant_course_access()
        return subscription

# class SubscriptionManager:
#     """Класс для управления подписками"""
#
#     def __init__(self, user: User):
#         self.user = user
#
#     def get_active_subscription(self):
#         """Получить активную подписку пользователя"""
#         now_date = now()
#         return Subscription.objects.filter(user=self.user, end_date__gte=now_date).first()
#
#     def is_subscription_active(self):
#         """Проверяет, есть ли активная подписка"""
#         return self.get_active_subscription() is not None
#
#     def cancel_subscription(self):
#         """Отменяет текущую подписку"""
#         subscription = self.get_active_subscription()
#         if subscription:
#             subscription.end_date = now()  # Устанавливаем дату окончания на текущее время
#             subscription.save()
#
#
# class CourseAccessManager:
#     """Класс для управления доступом к курсам"""
#
#     def __init__(self, user: User):
#         self.user = user
#
#     def get_accessible_courses(self):
#         """Получает список доступных курсов для пользователя"""
#         subscription = Subscription.objects.filter(user=self.user, end_date__gte=now()).first()
#         if not subscription:
#             return []
#
#         max_courses = subscription.plan.max_courses
#         return Course.objects.all()[:max_courses]
#
#     def has_access_to_course(self, course: Course):
#         """Проверяет, есть ли доступ к курсу"""
#         return course in self.get_accessible_courses()
