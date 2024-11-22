from django.core.management.base import BaseCommand
from users.models import PromoCode, SubscriptionPlan
import random
import string


def generate_promo_code(length=8):
    """Генерирует случайный уникальный промокод."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not PromoCode.objects.filter(code=code).exists():  # Проверка уникальности
            return code


class Command(BaseCommand):
    help = "Generate promo codes"

    def add_arguments(self, parser):
        parser.add_argument('--plan', type=str, required=True, help='Subscription Plan ID or Name')
        parser.add_argument('--duration', type=int, required=True, help='Duration in months')
        parser.add_argument('--max-uses', type=int, default=1, help='Maximum number of uses for each code')
        parser.add_argument('--count', type=int, default=10, help='Number of promo codes to generate')
        parser.add_argument('--length', type=int, default=8, help='Length of each promo code')

    def handle(self, *args, **kwargs):
        plan_name = kwargs['plan']
        duration = kwargs['duration']
        max_uses = kwargs['max_uses']
        count = kwargs['count']
        length = kwargs['length']

        try:
            # Находим план подписки
            plan = SubscriptionPlan.objects.get(name=plan_name)

            # Генерация промокодов
            codes = []
            for _ in range(count):
                code = generate_promo_code(length)
                PromoCode.objects.create(
                    code=code,
                    plan=plan,
                    duration=duration,
                    max_uses=max_uses,
                )
                codes.append(code)

            self.stdout.write(self.style.SUCCESS(f"Successfully generated {len(codes)} promo codes."))
            self.stdout.write("\n".join(codes))

        except SubscriptionPlan.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Subscription Plan '{plan_name}' not found."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
