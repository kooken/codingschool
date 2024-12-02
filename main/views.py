from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import PromoCode, SubscriptionPlan
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from main.forms import PromoCodeForm
import random
import string
from django.db.models import Q


def generate_promo_code(length=8):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not PromoCode.objects.filter(code=code).exists():
            return code


def activate_promo_code(request, promo_code_str):
    try:
        promo_code_instance = PromoCode.objects.get(code=promo_code_str)

        if not promo_code_instance.is_valid():
            messages.error(request, "Promo code is not valid or has already been used.")
            return False

        print(f"Promo code details: {promo_code_instance}")
        print(f"Subscription Plan: {promo_code_instance.plan}")
        print(f"Duration: {promo_code_instance.plan.duration.display_name}")
        print(f"User: {request.user}")
        print(f"Programming Languages: {promo_code_instance.programming_languages.all()}")
        print(f"Bonus Modules: {promo_code_instance.bonus_modules.all()}")

        now = timezone.now()

        duration_months = promo_code_instance.plan.duration.duration_in_months

        if duration_months is None:
            end_date = None
        else:
            end_date = now + relativedelta(months=duration_months)

        if end_date is not None:
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)
            else:
                end_date = timezone.localtime(end_date)

        print(f"End date calculated: {end_date}")

        try:
            subscription = promo_code_instance.plan
            subscription.is_active = True
            subscription.start_date = now
            subscription.end_date = end_date
            subscription.save()

            print(f"Subscription updated: {subscription}")

        except SubscriptionPlan.DoesNotExist:
            print("Error: Subscription plan not found.")
        except Exception as e:
            print(f"Error activating subscription: {str(e)}")

        promo_code_instance.is_active = False
        promo_code_instance.save()
        print(f"Is promocode activated? If true - not activated, if false - activated: {promo_code_instance.is_active}")

        messages.success(request, f"Promo code activated! Subscription starts on {subscription.start_date}")
        return True

    except PromoCode.DoesNotExist:
        messages.error(request, "Promo code not found.")
        return False
    except ValidationError as e:
        messages.error(request, str(e))
        return False
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return False


def promo_code_page(request):
    form = PromoCodeForm()
    promo_code_str = None
    activation_result = None

    if request.method == 'POST':
        if 'generate' in request.POST:
            form = PromoCodeForm(request.POST)
            if form.is_valid():
                plan = form.cleaned_data['plan']
                duration = form.cleaned_data['duration']
                programming_languages = form.cleaned_data['programming_languages']
                bonus_modules = form.cleaned_data['bonus_modules']

                print("Programming Languages from form:", programming_languages)
                print("Bonus Modules from form:", bonus_modules)

                try:
                    price_plan = {
                        'newbie': {
                            1: 10.0,
                        },
                        'middle': {
                            1: 15.0,
                            3: 40.0,
                            6: 75.0,
                        },
                        'pro': {
                            1: 30.0,
                            6: 160.0,
                            12: 300.0,
                            0: 400.0,
                        },
                    }

                    total_price = price_plan.get(plan.value, {}).get(duration.value)

                    if total_price is None:
                        raise ValueError(f"Price not found for plan: {plan.value}, duration: {duration.value}")

                    description = f"Includes {len(programming_languages)} programming language(s): " + \
                                  ", ".join(lang.display_name for lang in programming_languages) + \
                                  f" and {len(bonus_modules)} bonus module(s): " + \
                                  ", ".join(module.display_name for module in bonus_modules)

                    subscription_plan = SubscriptionPlan.objects.create(
                        user=request.user,
                        name=plan,
                        duration=duration,
                        description=description,
                        price=total_price,
                        is_active=False,
                    )

                    print("Created Subscription Plan:", subscription_plan)

                    subscription_plan.programming_languages.set(programming_languages)
                    subscription_plan.bonus_modules.set(bonus_modules)

                    print("Associated Programming Languages:", subscription_plan.programming_languages.all())
                    print("Associated Bonus Modules:", subscription_plan.bonus_modules.all())

                    print(f"Subscription updated: {subscription_plan}")

                    request.user.subscription_plan = subscription_plan
                    request.user.save()

                    if request.user.subscription_plan:
                        print(f"Subscription is related to user: {request.user.subscription_plan.name}")
                    else:
                        print("User has no subscription plan.")

                    promo_code_str = generate_promo_code(length=8)

                    # Создание промокода с выбранными параметрами
                    promo_code = PromoCode.objects.create(
                        code=promo_code_str,
                        plan=subscription_plan,
                        is_active=True,
                    )

                    promo_code.programming_languages.set(programming_languages)
                    promo_code.bonus_modules.set(bonus_modules)

                    print(f"Promo code generated: {promo_code_str}")
                    messages.success(request, f"Promo code generated: {promo_code_str}")

                except Exception as e:
                    print(f"Error occured: {str(e)}")
                    messages.error(request, f"Error: {str(e)}")

        elif 'activate' in request.POST:
            promo_code = request.POST.get('promo_code')
            activation_result = activate_promo_code(request, promo_code)
            if activation_result:
                messages.success(request, "Promo code activated successfully!")
            else:
                messages.error(request, "Error activating promo code.")

    return render(request, 'main/promo_code_page.html', {
        'form': form,
        'promo_code_str': promo_code_str,
        'activation_result': activation_result,
    })


@login_required
def user_dashboard(request):
    try:
        subscription = SubscriptionPlan.objects.filter(
            Q(user=request.user) & (Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True))
        ).first()

        if subscription:
            print(f"Active subscription found: {subscription}")
        else:
            print("No active subscription found.")
    except SubscriptionPlan.DoesNotExist:
        print("No active subscription found.")

    return render(request, 'main/user_dashboard.html', {'subscription': subscription})


def index(request):
    return render(request, 'main/index.html')


def courses(request):
    courses_data = [
        {
            'name': 'Go',
            'image': 'main/css/images/golang-course.png',
            'description': 'Go, also known as Golang, is a statically typed, compiled programming language designed at Google. It\'s known for its simplicity, concurrency support, and performance.'
        },
        {
            'name': 'Python',
            'image': 'main/css/images/python-course.png',
            'description': 'Python is an interpreted, high-level, general-purpose programming language. It emphasizes code readability and has a vast ecosystem of libraries.'
        },
        {
            'name': 'C',
            'image': 'main/css/images/c-course.png',
            'description': 'C is a powerful general-purpose programming language. It is widely used in systems programming, game development, and embedded systems.'
        },
        {
            'name': 'JavaScript',
            'image': 'main/css/images/javascript-course.png',
            'description': 'JavaScript is a versatile, high-level language commonly used in web development to add interactivity to web pages.'
        },
        {
            'name': 'SQL',
            'image': 'main/css/images/sql-course.png',
            'description': 'SQL, or Structured Query Language, is a standardized language for managing and querying relational databases.'
        }
    ]

    return render(request, 'main/courses.html', {'courses_data': courses_data})


def mission(request):
    return render(request, 'main/mission.html')


def community(request):
    return render(request, 'main/community.html')


def job_search(request):
    return render(request, 'main/job_search.html')


def team(request):
    return render(request, 'main/team.html')


def test(request):
    return render(request, 'main/test.html')
