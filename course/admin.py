from django.contrib import admin
from course.models import Course, Lesson
from users.models import SubscriptionPlan, UserSubscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    search_fields = ('title',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(UserSubscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date')
    search_fields = ('user__email',)
