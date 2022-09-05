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
# from projects.models import Projects
from django.db.models import Q, Count

class Patients(models.Model):
    pat_id = models.CharField(max_length=12, blank=False, null=False, unique=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    # age = models.FloatField(blank=True, null=True)
    dob = models.IntegerField(blank=True, null=True)
    race = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=20, blank=True, null=True)
    blocks_temp = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    pa_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(auto_now=True)

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
                '1': 'pat_id',
                '2': 'sex',
                '3': 'race',
                '4': 'source',
                '5': 'project',
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
                    Q(source__icontains=search_value) |
                    Q(project__icontains=search_value))

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

class Areas(models.Model):
    PUNCH = 'PU'
    SCRAPE = 'SC'
    PELLET = 'PE'
    CURLS = 'CU'
    COLLECTION_CHOICES = [
        (PUNCH, 'Punch'),
        (SCRAPE, 'Scraping'),
        (PELLET, 'Cell Pellet'),
        (CURLS, 'Curls')
    ]
    IN_SITU = 'IS'
    INVASIVE = 'INV'
    NORMAL = 'N'
    BENIGN = 'B'
    INTERMEDIATE = 'INT'
    STROMA = 'ST'
    TUMOR = 'T'
    TYPE_CHOICES = [
        (TUMOR, 'Malignant Tumor, NOS'),
        (IN_SITU, 'Malignant Tumor, In Situ'),
        (INVASIVE, 'Malignant Tumor, Invasive'),
        (BENIGN, 'Benign Tumor (e.g. Nevus)'),
        (NORMAL, 'Normal'),
        (STROMA, 'Stroma'),
        (INTERMEDIATE, 'Intermediate Tumor')
    ]
    old_area_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    area = models.CharField(max_length=6, blank=True, null=True)
    old_block_id = models.CharField(max_length=50, blank=True, null=True)
    collection = models.CharField(max_length=2, choices=COLLECTION_CHOICES, default=SCRAPE, blank=True, null=True)
    area_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TUMOR, blank=False, null=False)
    he_image = models.CharField(max_length=200, blank=True, null=True)
    na_id = models.CharField(max_length=50, blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True, default=date.today)
    investigator = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/%y/%m/%d")
    notes = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    block = models.ForeignKey('blocks.Blocks', on_delete=models.CASCADE, db_column='block', blank=True, null=True, related_name="block_areas")
    ar_id = models.AutoField(primary_key=True)

    class Meta:
        managed = True
        db_table = 'areas'

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         Areas.old_block_id = Blocks.old_block_id
    #         print('Hello:', Areas.old_block_id)
    #     super().save(*args, **kwargs)
