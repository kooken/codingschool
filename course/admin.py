from django.contrib import admin
from course.models import Course, Lesson, Homework, HomeworkSubmission
from users.models import SubscriptionPlan


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at',
                    'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('programming_languages', 'bonus_modules',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'user', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status',)
    readonly_fields = ('homework', 'user', 'github_link', 'submitted_at')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not request.user.groups.filter(name='teachers').exists():
            return self.readonly_fields + ('status', 'reviewed_at')
        return self.readonly_fields


admin.site.register(HomeworkSubmission, HomeworkSubmissionAdmin)


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
