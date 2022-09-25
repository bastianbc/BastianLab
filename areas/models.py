from django.db import models
from django.db.models import Q, Count
from datetime import date
import uuid

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

    def __str__(self):
        return "%d" % self.ar_id

    def _generate_unique_id(self):
        return str(uuid.uuid4())

    def save(self,*args,**kwargs):
        if not self.old_area_id:
            self.old_area_id = self._generate_unique_id()

        super().save(*args, **kwargs)

    def query_by_args(self, **kwargs):

        def _parse_value(search_value):
            if "_initial:" in search_value:
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "1":"ar_id",
                "2":"area",
                "3":"old_area_id",
                "4":"old_block_id",
                "5":"collection",
                "6":"area_type",
                "7":"he_image",
                "8":"na_id",
                "9":"completion_date",
                "10":"investigator",
                "11":"project",
                "12":"block",
                "13":"notes",
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

            queryset = Areas.objects.all().annotate(num_nucacids=Count('area_nucacids'))
            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if is_initial:
                queryset = queryset.filter(
                        Q(block__bl_id=search_value)
                    )
            elif search_value:
                queryset = queryset.filter(
                        Q(ar_id__icontains=search_value) |
                        Q(na_id__icontains=search_value) |
                        Q(area__icontains=search_value) |
                        Q(investigator__icontains=search_value) |
                        Q(notes__icontains=search_value) |
                        Q(project__icontains=search_value)
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
