from django.contrib import admin
from course.models import Course, Lesson, Homework
from users.models import SubscriptionPlan


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at',
                    'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('programming_languages', 'bonus_modules',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'task_description')
