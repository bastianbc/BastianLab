# Generated by Django 3.2.15 on 2024-02-18 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patients',
            fields=[
                ('pat_id', models.CharField(help_text='Requires a unique identifier for each patient.', max_length=12, unique=True, verbose_name='Patient ID')),
                ('sex', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female')], max_length=1, null=True, verbose_name='Sex')),
                ('dob', models.IntegerField(blank=True, null=True, verbose_name='Birthyear')),
                ('race', models.SmallIntegerField(blank=True, choices=[(1, 'American Indian or Alaska Native'), (2, 'Asian'), (3, 'Black or African American'), (4, 'Native Hawaiian or Other Pacific Islander'), (5, 'White'), (6, 'Hispanic/Latino/Spanish Origin (of any race)'), (7, 'N/A')], default=7, null=True)),
                ('source', models.CharField(blank=True, max_length=20, null=True, verbose_name='Source')),
                ('blocks_temp', models.CharField(blank=True, max_length=100, null=True, verbose_name='Blocks')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('pa_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
                'db_table': 'patients',
                'managed': True,
            },
        ),
    ]
