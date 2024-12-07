from django import forms
from django_select2 import forms as s2forms
from course.models import Comment, HomeworkSubmission, HomeworkSubmissionStatuses


class LessonTestForm(forms.Form):
    def __init__(self, questions=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if questions:
            for index, question in enumerate(questions, start=1):
                self.fields[f'question_{index}'] = forms.ChoiceField(
                    label=question['question'],
                    choices=[(choice, choice) for choice in question['answer_choices']],
                    widget=forms.RadioSelect,
                    required=True
                )

    def clean(self):
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            field_choices = self.fields[field_name].choices
            if value not in dict(field_choices):
                cleaned_data[field_name] = None
        return cleaned_data


class HomeworkStatusSelect2Widget(s2forms.ModelSelect2Widget):
    search_fields = [
        'value__icontains',
    ]

    def get_queryset(self):
        return HomeworkSubmissionStatuses.objects.all()


class HomeworkSubmissionFormAdmin(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['status', 'reviewed_at', 'comment']
        widgets = {
            'status': HomeworkStatusSelect2Widget(
                attrs={'class': 'django-select2'},
            ),
            'reviewed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your comment...'}),
        }

    comment = forms.CharField(required=False)


class HomeworkSubmissionFormStudent(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['github_link']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your comment...'}),
        }
