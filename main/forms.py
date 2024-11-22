from django import forms
from users.models import SubscriptionPlan, ProgrammingLanguage, BonusModule


class PromoCodeForm(forms.Form):
    # Поле для выбора плана подписки
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.all(),  # Отображаем все планы подписки
        label="Select Plan",
        required=True
    )

    # Поле для выбора длительности подписки
    duration = forms.ChoiceField(
        choices=[(1, '1 Month'), (3, '3 Months'), (6, '6 Months'), (12, '1 Year'), ('forever', 'Forever')],
        label="Duration",
        required=True
    )

    # Поле для выбора языков программирования
    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),  # Показываем все языки
        widget=forms.CheckboxSelectMultiple,
        label="Programming Languages",
        required=True
    )

    # Поле для выбора бонусных модулей
    bonus_modules = forms.ModelMultipleChoiceField(
        queryset=BonusModule.objects.all(),  # Показываем все бонусные модули
        widget=forms.CheckboxSelectMultiple,
        label="Bonus Modules",
        required=True
    )
