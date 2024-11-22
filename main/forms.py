from django import forms
from users.models import SubscriptionPlanModes, ProgrammingLanguage, BonusModule, SubscriptionDurationTypes


class PromoCodeForm(forms.Form):
    # Поле для выбора плана подписки
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlanModes.objects.all(),  # Отображаем все планы подписки
        label="Select Subscription Plan",  # Уникальная метка
        required=True
    )

    # Поле для выбора длительности подписки
    duration = forms.ModelChoiceField(
        queryset=SubscriptionDurationTypes.objects.all(),  # Отображаем все длительности подписки
        label="Select Subscription Duration",  # Уникальная метка
        required=True
    )

    # Поле для выбора языков программирования
    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),  # Показываем все языки
        widget=forms.CheckboxSelectMultiple,
        label="Select Programming Languages",
        required=True
    )

    # Поле для выбора бонусных модулей
    bonus_modules = forms.ModelMultipleChoiceField(
        queryset=BonusModule.objects.all(),  # Показываем все бонусные модули
        widget=forms.CheckboxSelectMultiple,
        label="Select Bonus Modules",
        required=True
    )
