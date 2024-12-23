# Generated by Django 5.1.3 on 2024-11-27 18:39

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_subscriptiondurationtypes_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='Is Active'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Start Date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='subscription_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='bonus_modules',
            field=models.ManyToManyField(blank=True, related_name='subscription_bonus_modules', to='users.bonusmodule'),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='duration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_duration', to='users.subscriptiondurationtypes', verbose_name='Subscription Duration'),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_plan_name', to='users.subscriptionplanmodes', verbose_name='Subscription Plan Name'),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='programming_languages',
            field=models.ManyToManyField(blank=True, related_name='subscription_prog_langs', to='users.programminglanguage'),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscription_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_subscription_plan', to='users.subscriptionplan'),
        ),
        migrations.DeleteModel(
            name='UserSubscription',
        ),
    ]
