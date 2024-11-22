from django.core.management.base import BaseCommand
from users.models import PromoCode, SubscriptionPlan, ProgrammingLanguage, BonusModule
import random
import string


def generate_promo_code():
    """Генерирует случайный уникальный промокод с фиксированной длиной 8 символов."""
    length = 8  # Фиксированная длина
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not PromoCode.objects.filter(code=code).exists():  # Проверка уникальности
            return code


class Command(BaseCommand):
    help = "Generate promo codes with specified parameters"

    def add_arguments(self, parser):
        parser.add_argument('--plan', type=str, required=True, help="Subscription Plan ID or Name")
        parser.add_argument('--duration', type=int, required=True, help="Duration in months")
        parser.add_argument('--languages', nargs='+', type=str, required=False, help="List of programming languages")
        parser.add_argument('--bonus-modules', nargs='+', type=str, required=False, help="List of bonus module IDs")

    def handle(self, *args, **kwargs):
        plan_name = kwargs['plan']
        duration = kwargs['duration']
        languages = kwargs.get('languages', [])
        bonus_modules = kwargs.get('bonus_modules', [])

        try:
            # Найти план подписки
            plan = SubscriptionPlan.objects.get(name=plan_name)

            # Найти языки программирования
            programming_languages = ProgrammingLanguage.objects.filter(value__in=languages)
            if len(programming_languages) != len(languages):
                raise ValueError("One or more programming languages not found.")

            # Найти бонусные модули
            bonus_modules_objects = BonusModule.objects.filter(name__in=bonus_modules)
            if len(bonus_modules_objects) != len(bonus_modules):
                raise ValueError("One or more bonus modules not found.")

            # Генерация одного промокода
            promo_code_str = generate_promo_code()
            promo_code = PromoCode.objects.create(
                code=promo_code_str,
                plan=plan,
                duration=duration,
                is_active=True,  # Промокод активен по умолчанию
            )

            # Установка языков программирования и бонусных модулей
            promo_code.programming_languages.set(programming_languages)
            promo_code.bonus_modules.set(bonus_modules_objects)

            self.stdout.write(self.style.SUCCESS(f"Promo code generated: {promo_code_str}"))

        except SubscriptionPlan.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Subscription Plan '{plan_name}' not found."))
        except ValueError as ve:
            self.stderr.write(self.style.ERROR(str(ve)))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
