# Generated by Django 5.1.3 on 2024-11-22 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_add_subscription_duration_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]