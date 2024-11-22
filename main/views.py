from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import PromoCode, UserSubscription, SubscriptionPlan, ProgrammingLanguage, BonusModule
from datetime import timedelta
from main.forms import PromoCodeForm
from main.management.commands.generate_coupons import generate_promo_code


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

def promo_code_page(request):
    form = PromoCodeForm()  # создаем пустую форму

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
                    # Генерация одного промокода
                    promo_code_str = generate_promo_code(length=8)  # Длина промокода всегда 8

                    # Создание промокода с выбранными параметрами
                    promo_code = PromoCode.objects.create(
                        code=promo_code_str,
                        plan=plan,
                        duration=duration,
                        max_uses=1,  # Промокод одноразовый
                    )

                    # Ассоциируем языки программирования и бонусные модули с промокодом
                    promo_code.programming_languages.set(programming_languages)
                    promo_code.bonus_modules.set(bonus_modules)

                    # Отображаем успешное сообщение
                    messages.success(request, f"Promo code generated: {promo_code_str}")

                except Exception as e:
                    messages.error(request, str(e))

        elif 'activate' in request.POST:
            # Активация промокода
            promo_code = request.POST.get('promo_code')
            try:
                promo_code_instance = PromoCode.objects.get(code=promo_code)

                if not promo_code_instance.is_valid():
                    raise Exception("Promo code is not valid or has already been used.")

                # Создаем или обновляем подписку для пользователя
                UserSubscription.objects.create(
                    user=request.user,
                    plan=promo_code_instance.plan,
                    start_date=request.user.date_joined,  # Можно использовать дату регистрации пользователя или текущую
                    end_date=request.user.date_joined + timedelta(months=promo_code_instance.duration),
                    programming_languages=promo_code_instance.programming_languages.all(),
                    bonus_modules=promo_code_instance.bonus_modules.all()
                )

                # Активируем промокод (одноразовое использование)
                promo_code_instance.uses += 1
                promo_code_instance.save()

                messages.success(request, "Promo code activated and subscription applied!")
            except PromoCode.DoesNotExist:
                messages.error(request, "Promo code not found.")
            except Exception as e:
                messages.error(request, str(e))

        return redirect('main:promo_code_page')

    return render(request, 'main/promo_code_page.html', {'form': form})

    return render(request, 'main/promo_code_page.html', {
        'form': form,
        'subscription_plans': subscription_plans,
        'programming_languages': programming_languages,
        'bonus_modules': bonus_modules
    })


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
