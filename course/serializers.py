from rest_framework import serializers
from .models import Lesson, LessonTestResult, HomeworkSubmission, LessonTestQuestion


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonTestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTestQuestion
        fields = '__all__'


class LessonTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTestResult
        fields = '__all__'


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = '__all__'
