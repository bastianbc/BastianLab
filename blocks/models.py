from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, Count

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
    patient = models.ForeignKey('lab.Patients', on_delete=models.CASCADE, db_column='patient', blank=True, null=True, related_name="patient_blocks")
    bl_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        db_table = 'blocks'
        managed = True

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                "1":"patient",
                "2":"diagnosis",
                "3":"body_site",
                "4":"gross",
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

            queryset = Blocks.objects.all().annotate(num_areas=Count('block_areas'))
            total = queryset.count()

            if search_value:
                queryset = queryset.filter(
                    Q(patient__pat_id__icontains=search_value) |
                    Q(diagnosis__icontains=search_value) |
                    Q(body_site__icontains=search_value) |
                    Q(gross__icontains=search_value))

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
