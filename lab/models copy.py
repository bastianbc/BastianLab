from django.db import models
from django.urls import reverse


# def pkgen():
#     from base64 import b32encode
#     from hashlib import sha1
#     from random import random
#     # rude = ('lol',)
#     bad_pk = True
#     while bad_pk:
#         pk = b32encode(sha1(str(random())).digest()).lower()[:8]
#         bad_pk = False
#         # for rw in rude:
#         #     if pk.find(rw) >= 0: bad_pk = True
#     return pk

class Tpats(models.Model):
    name  = models.CharField(max_length=50)
    age = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    notes = models.CharField(max_length=50,blank=True)

class Patients(models.Model):
    pat_id = models.CharField(primary_key=True, max_length=12)
    sex = models.CharField(max_length=1, blank=True, null=True)
    age = models.FloatField(blank=True, null=True)
    race = models.CharField(max_length=1, blank=True, null=True)
    source = models.CharField(max_length=20, blank=True, null=True)
    blocks_temp = models.CharField(max_length=100, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('patient-update', kwargs={'pk': self.pk})

    class Meta:
        managed = True
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Blocks(models.Model):
    block_id = models.CharField(primary_key=True, max_length=50)
    pat_id = models.ForeignKey('Patients', models.CASCADE, blank=True, null=True)
    body_site = models.CharField(max_length=200, blank=True, null=True)
    ulceration = models.BooleanField(blank=True, null=True)
    slides = models.IntegerField(blank=True, null=True)
    slides_left = models.IntegerField(blank=True, null=True)
    fixation = models.CharField(max_length=10, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    diagnosis = models.CharField(max_length=50, blank=True, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    receive = models.DateField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'blocks'
        
class Areas(models.Model):
    area_id = models.CharField(primary_key=True, max_length=50)
    area = models.CharField(max_length=6, blank=True, null=True)
    block = models.ForeignKey('Blocks', models.CASCADE, blank=True, null=True)
    collection = models.CharField(max_length=50, blank=True, null=True)
    area_type = models.CharField(max_length=50, blank=True, null=True)
    he_image = models.CharField(max_length=200, blank=True, null=True)
    completion_date = models.CharField(max_length=20, blank=True, null=True)
    investigator = models.CharField(max_length=50, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'areas'