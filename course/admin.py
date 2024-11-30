from django.contrib import admin
from course.models import Course, Lesson, Homework
from users.models import SubscriptionPlan


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at',
                    'updated_at')  # Добавляем язык программирования и дату обновления
    search_fields = ('title', 'description')  # Добавляем описание в поиск
    list_filter = ('programming_languages', 'bonus_modules',)  # Добавляем фильтр по языку программирования
    ordering = ('-created_at',)  # Сортировка по дате создания (по убыванию)
    date_hierarchy = 'created_at'  # Дает возможность фильтровать по дате


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
