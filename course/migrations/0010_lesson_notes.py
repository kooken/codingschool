# Generated by Django 5.1.3 on 2024-12-08 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_alter_homeworksubmission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='notes',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
