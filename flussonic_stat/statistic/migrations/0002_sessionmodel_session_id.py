# Generated by Django 3.2.8 on 2021-10-30 19:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionmodel',
            name='session_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=54),
            preserve_default=False,
        ),
    ]
