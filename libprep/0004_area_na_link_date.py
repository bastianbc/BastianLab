# Generated by Django 2.2.15 on 2024-01-17 22:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libprep', '0003_remove_nucacids_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='area_na_link',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Date'),
        ),
    ]