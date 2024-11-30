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


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['github_link']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # только текст комментария
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your comment...'}),
        }
