# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from projects.models import Projects
from decimal import Decimal
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.db.models import Q, Count

class Patients(models.Model):

    RACE_TYPES = (
        (1, "American Indian or Alaska Native"),
        (2, "Asian"),
        (3, "Black or African American"),
        (4, "Native Hawaiian or Other Pacific Islander"),
        (5, "White"),
        (6, "Hispanic/Latino/Spanish Origin (of any race)"),
        (7, "N/A"),
    )

    SEX_TYPES = (
        ("m","Male"),
        ("f","Female"),
    )

    pat_id = models.CharField(max_length=12, blank=False, null=False, unique=True, verbose_name="Patient ID", help_text="Requires a unique identifier for each patient.")
    sex = models.CharField(max_length=1, choices=SEX_TYPES, blank=True, null=True, verbose_name="Sex")
    # age = models.FloatField(blank=True, null=True)
    dob = models.IntegerField(blank=True, null=True, verbose_name="Birthyear")
    race = models.SmallIntegerField(choices=RACE_TYPES, default=1, blank=True, null=True)
    # race = models.CharField(max_length=200,blank=True, null=True, verbose_name="Race")
    source = models.CharField(max_length=20, blank=True, null=True, verbose_name="Source")
    blocks_temp = models.CharField(max_length=100, blank=True, null=True, verbose_name="Blocks")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    # project = models.CharField(max_length=50, blank=True, null=True, verbose_name="Project")
    pa_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def get_absolute_url(self):
        return reverse('patient-update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.pat_id

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'pa_id',
                '1': 'pat_id',
                '2': 'sex',
                '3': 'race',
                '4': 'source',
                '5': 'date_added'
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = Patients.objects.all().annotate(num_blocks=Count('patient_blocks'))
            total = queryset.count()

            if search_value:
                queryset = queryset.filter(
                    Q(pat_id__icontains=search_value) |
                    Q(race__icontains=search_value) |
                    Q(source__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            # queryset = queryset[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise
