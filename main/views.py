from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import PromoCode, UserSubscription, SubscriptionPlan, SubscriptionPlanModes
from datetime import timedelta
from main.forms import PromoCodeForm
import random
import string


# class PromoCodeActivationView(View):
#     """Вью для активации промокодов"""
#
#     def post(self, request, *args, **kwargs):
#         promo_code = request.POST.get('promo_code')
#         user = request.user
#
#         try:
#             handler = PromoCodeHandler(user, promo_code)
#             subscription = handler.process()
#
#             messages.success(request, f"Subscription activated successfully! Plan: {subscription.plan.name}")
#             return redirect('dashboard')
#
#         except ValidationError as e:
#             messages.error(request, str(e))
#             return redirect('promo_code_activation')
#
#     def get(self, request, *args, **kwargs):
#         return render(request, 'promo_code_activation.html')


# class DashboardView(View):
#     """Личный кабинет пользователя"""
#
#     def get(self, request, *args, **kwargs):
#         course_manager = CourseAccessManager(request.user)
#         accessible_courses = course_manager.get_accessible_courses()
#
#         return render(request, 'dashboard.html', {'courses': accessible_courses})

# Генерация случайного уникального промокода
def generate_promo_code(length=8):
    """Генерирует случайный уникальный промокод с фиксированной длиной."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not PromoCode.objects.filter(code=code).exists():  # Проверка уникальности
            return code


from dateutil.relativedelta import relativedelta


def activate_promo_code(request, promo_code_str):
    """Функция для активации промокода."""
    try:
        # Находим промокод по строке
        promo_code_instance = PromoCode.objects.get(code=promo_code_str)

        # Проверяем, что промокод активен
        if not promo_code_instance.is_active:
            raise Exception("Promo code is not valid or has already been used.")

        # Проверяем, если подписка бессрочная
        if promo_code_instance.plan.duration is None:
            end_date = None  # Подписка бессрочная
        else:
            # Получаем длительность подписки как число месяцев
            duration_months = int(promo_code_instance.plan.duration.value)  # Преобразуем в целое число
            end_date = request.user.date_joined + relativedelta(months=duration_months)

        # Создаем подписку для пользователя
        user_subscription = UserSubscription.objects.create(
            user=request.user,
            plan=promo_code_instance.plan,
            start_date=request.user.date_joined,
            end_date=end_date,  # Если бессрочная, то None
        )

        # Ассоциируем языки программирования и бонусные модули с подпиской
        user_subscription.programming_languages.set(promo_code_instance.programming_languages.all())
        user_subscription.bonus_modules.set(promo_code_instance.bonus_modules.all())

        # Делаем промокод неактивным (он одноразовый)
        promo_code_instance.is_active = False
        promo_code_instance.save()

        # Сообщение об успешной активации
        messages.success(request, "Promo code activated and subscription applied!")

        return True  # Успешная активация

    except PromoCode.DoesNotExist:
        messages.error(request, "Promo code not found.")
    except Exception as e:
        messages.error(request, str(e))

    return False  # В случае ошибки


def promo_code_page(request):
    form = PromoCodeForm()  # Создаем пустую форму

    if request.method == 'POST':
        if 'generate' in request.POST:
            form = PromoCodeForm(request.POST)
            if form.is_valid():
                # Получаем данные от пользователя для генерации промокода
                plan = form.cleaned_data['plan']
                duration = form.cleaned_data['duration']
                programming_languages = form.cleaned_data['programming_languages']
                bonus_modules = form.cleaned_data['bonus_modules']

                try:
                    # Создаем SubscriptionPlan на основе данных пользователя
                    subscription_plan = SubscriptionPlan.objects.create(
                        name=plan,  # Название плана подписки
                        duration=duration,  # Длительность подписки
                        description="Generated Subscription Plan",  # Можно сделать описание динамическим
                        price=0.0,  # Цена на этапе генерации промокода
                    )

                    # Ассоциируем языки программирования и бонусные модули с созданным планом подписки
                    subscription_plan.programming_languages.set(programming_languages)
                    subscription_plan.bonus_modules.set(bonus_modules)

                    # Генерация одного промокода
                    promo_code_str = generate_promo_code(length=8)  # Длина промокода всегда 8

                    # Создание промокода с выбранными параметрами
                    promo_code = PromoCode.objects.create(
                        code=promo_code_str,
                        plan=subscription_plan,  # Привязываем только что созданный план подписки
                        is_active=True,  # По умолчанию промокод активен
                    )

                    # Ассоциируем языки программирования и бонусные модули с промокодом
                    promo_code.programming_languages.set(programming_languages)
                    promo_code.bonus_modules.set(bonus_modules)

                    # Отображаем успешное сообщение
                    messages.success(request, f"Promo code generated: {promo_code_str}")

                except Exception as e:
                    messages.error(request, str(e))

        elif 'activate' in request.POST:
            # Активируем промокод
            promo_code = request.POST.get('promo_code')
            if activate_promo_code(request, promo_code):
                return redirect('main:user_dashboard')  # Перенаправляем на личный кабинет после активации

        return redirect('main:promo_code_page')  # Перенаправляем на страницу после успешной генерации

    return render(request, 'main/promo_code_page.html', {'form': form})


@login_required
def user_dashboard(request):
    # Получаем все подписки пользователя
    subscriptions = UserSubscription.objects.filter(user=request.user)

    return render(request, 'main/user_dashboard.html', {'subscriptions': subscriptions})


def index(request):
    return render(request, 'main/index.html')


def courses(request):
    return render(request, 'main/courses.html')


def mission(request):
    return render(request, 'main/mission.html')


def community(request):
    return render(request, 'main/community.html')


def job_search(request):
    return render(request, 'main/job_search.html')


def team(request):
    return render(request, 'main/team.html')
