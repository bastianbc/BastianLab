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
from django.core.validators import MinValueValidator, MaxValueValidator
# from projects.models import Projects



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

    def get_absolute_url(self):
        return reverse('patient-update', kwargs={'pk': self.pk})

    class Meta:
        managed = True
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

class Blocks(models.Model):
    old_block_id = models.CharField(max_length=50, blank=True, null=False, unique=True)
    pat_id = models.CharField(max_length=12, blank=True, null=True)
    age = models.DecimalField(blank=True, null=True, decimal_places=1, max_digits=4, validators=[
        MinValueValidator((0.1), message='Minimum age is 0.1 years'),
        MaxValueValidator((120), message='Maximum age is 120 years'),
        ])
    body_site = models.TextField(blank=True, null=True)
    ulceration = models.BooleanField(blank=True, null=True)
    thickness = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    mitoses = models.IntegerField(blank=True, null=True)
    p_stage = models.TextField(blank=True, null=True)
    prim = models.TextField(blank=True, null=True)
    subtype = models.TextField(blank=True, null=True)
    slides = models.IntegerField(blank=True, null=True)
    slides_left = models.IntegerField(blank=True, null=True)
    fixation = models.CharField(max_length=10, blank=True, null=True)
    area_id = models.CharField(max_length=100, blank=True, null=True)
    old_project = models.CharField(max_length=50, blank=True, null=True)
    project = models.ForeignKey('projects.Projects', on_delete=models.DO_NOTHING, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    micro = models.TextField(blank=True, null=True)
    gross = models.TextField(blank=True, null=True)
    clinical = models.TextField(blank=True, null=True)
    site_code = models.TextField(blank=True, null=True)
    icd9 = models.TextField(blank=True, null=True)
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE, db_column='patient', blank=True, null=True)
    bl_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'blocks'


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
    block = models.ForeignKey('Blocks', on_delete=models.CASCADE, db_column='block', blank=True, null=True)
    ar_id = models.AutoField(primary_key=True)

    class Meta:
        managed = True
        db_table = 'areas'
        
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         Areas.old_block_id = Blocks.old_block_id
    #         print('Hello:', Areas.old_block_id)
    #     super().save(*args, **kwargs)

