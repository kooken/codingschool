# Generated by Django 5.1.3 on 2024-12-08 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_lesson_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='notes',
            field=models.FileField(blank=True, null=True, upload_to='lesson_json_notes/'),
        ),
    ]
