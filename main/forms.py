from django import forms
from users.models import SubscriptionPlanModes, ProgrammingLanguage, BonusModule, SubscriptionDurationTypes


class PromoCodeForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlanModes.objects.all(),
        label="Select Subscription Plan",
        required=True
    )

    duration = forms.ModelChoiceField(
        queryset=SubscriptionDurationTypes.objects.all(),
        label="Select Subscription Duration",
        required=True
    )

    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Programming Languages",
        required=True
    )

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
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.filter(value="1 month")

            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()
            self.fields['programming_languages'].widget = forms.Select()
            self.fields['programming_languages'].required = True

            self.fields['bonus_modules'].queryset = BonusModule.objects.filter(name__in=["LinkedIn", "GitHub"])

        elif selected_plan == 'middle':
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.exclude(name__in=["1 year", "Forever"])

            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()
            self.fields[
                'programming_languages'].widget = forms.CheckboxSelectMultiple()
            self.fields['programming_languages'].required = True

            self.fields['bonus_modules'].queryset = BonusModule.objects.filter(
                name__in=["LinkedIn", "GitHub", "Docker", "Django"])

        elif selected_plan == 'pro':
            self.fields['duration'].queryset = SubscriptionDurationTypes.objects.all()

            self.fields['programming_languages'].queryset = ProgrammingLanguage.objects.all()

            self.fields['bonus_modules'].queryset = BonusModule.objects.all()

    def clean_programming_languages(self):
        programming_languages = self.cleaned_data['programming_languages']
        plan = self.cleaned_data.get('plan')
        if plan and plan.value == 'middle' and len(programming_languages) > 3:
            raise forms.ValidationError("You can select up to 3 programming languages for the 'middle' plan.")
        elif plan and plan.value == 'newbie' and len(programming_languages) > 1:
            raise forms.ValidationError("You can select only 1 programming language for the 'newbie' plan.")

        return programming_languages
