from django.db import models
from django.db.models import Q, Count
from datetime import date

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
        db_table = 'areas'

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         Areas.old_block_id = Blocks.old_block_id
    #         print('Hello:', Areas.old_block_id)
    #     super().save(*args, **kwargs)
