from django import forms

from course.models import Comment, HomeworkSubmission


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


class HomeworkSubmissionForm(forms.ModelForm):
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
