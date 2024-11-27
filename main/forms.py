from django import forms
from users.models import SubscriptionPlanModes, ProgrammingLanguage, BonusModule, SubscriptionDurationTypes


class PromoCodeForm(forms.Form):
    # Поле для выбора плана подписки
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlanModes.objects.all(),
        label="Select Subscription Plan",
        required=True
    )

    # Поле для выбора длительности подписки
    duration = forms.ModelChoiceField(
        queryset=SubscriptionDurationTypes.objects.all(),
        label="Select Subscription Duration",
        required=True
    )

    # Поле для выбора языков программирования
    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Programming Languages",
        required=True
    )

    # Поле для выбора бонусных модулей
    bonus_modules = forms.ModelMultipleChoiceField(
        queryset=BonusModule.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Bonus Modules",
        required=True
    )

    def __init__(self, *args, **kwargs):
        selected_plan = kwargs.pop('selected_plan', None)
        super().__init__(*args, **kwargs)
        if selected_plan == 'newbie':
            # Ограничиваем выбор длительности подписки до 1 месяца
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.filter(value="1 month")

            # Ограничиваем выбор языков программирования до 1 (позволяем только 1 язык)
            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()
            self.fields['programming_languages'].widget = forms.Select()  # Принудительно используем выпадающий список
            self.fields['programming_languages'].required = True  # Обязательно выбрать 1 язык

            # Ограничиваем выбор бонусных модулей до LinkedIn и GitHub
            self.fields['bonus_modules'].queryset = BonusModule.objects.filter(name__in=["LinkedIn", "GitHub"])

        elif selected_plan == 'middle':
            # Ограничиваем выбор длительности подписки (исключаем 1 год и forever)
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.exclude(name__in=["1 year", "Forever"])

            # Ограничиваем выбор языков программирования до 3
            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()
            self.fields[
                'programming_languages'].widget = forms.CheckboxSelectMultiple()  # Позволяет выбрать несколько языков
            self.fields['programming_languages'].required = True  # Обязательно выбрать хотя бы 1 язык

            # Ограничиваем выбор бонусных модулей (добавляем Docker и Django)
            self.fields['bonus_modules'].queryset = BonusModule.objects.filter(
                name__in=["LinkedIn", "GitHub", "Docker", "Django"])

        elif selected_plan == 'pro':
            # Все длительности доступны
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.all()

            # Все языки программирования доступны
            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()

            # Все бонусные модули доступны
            self.fields['bonus_modules'].queryset = BonusModule.objects.all()

    def clean_programming_languages(self):
        programming_languages = self.cleaned_data['programming_languages']
        plan = self.cleaned_data.get('plan')  # Получаем выбранный план подписки

        if plan and plan.value == 'middle' and len(programming_languages) > 3:
            raise forms.ValidationError("You can select up to 3 programming languages for the 'middle' plan.")
        elif plan and plan.value == 'newbie' and len(programming_languages) > 1:
            raise forms.ValidationError("You can select only 1 programming language for the 'newbie' plan.")

        return programming_languages

# class PromoCodeForm(forms.Form):
#     # Поле для выбора плана подписки
#     plan = forms.ModelChoiceField(
#         queryset=SubscriptionPlanModes.objects.all(),  # Отображаем все планы подписки
#         label="Select Subscription Plan",  # Уникальная метка
#         required=True
#     )
#
#     # Поле для выбора длительности подписки
#     duration = forms.ModelChoiceField(
#         queryset=SubscriptionDurationTypes.objects.all(),  # Отображаем все длительности подписки
#         label="Select Subscription Duration",  # Уникальная метка
#         required=True
#     )
#
#     # Поле для выбора языков программирования
#     programming_languages = forms.ModelMultipleChoiceField(
#         queryset=ProgrammingLanguage.objects.all(),  # Показываем все языки
#         widget=forms.CheckboxSelectMultiple,
#         label="Select Programming Languages",
#         required=True
#     )
#
#     # Поле для выбора бонусных модулей
#     bonus_modules = forms.ModelMultipleChoiceField(
#         queryset=BonusModule.objects.all(),  # Показываем все бонусные модули
#         widget=forms.CheckboxSelectMultiple,
#         label="Select Bonus Modules",
#         required=True
#     )
