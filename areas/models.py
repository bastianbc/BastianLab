from django.db import models
from django.db.models import Q, Count
from datetime import date
from django.utils.crypto import get_random_string

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

    AREA_TYPE_TYPES = (
        ("mel1","Mel 1"),
        ("mel2","Mel 2"),
        ("mel3","Mel 3"),
        ("mel4","Mel 4"),
        ("in_situ","in situ"),
        ("nevus1","Nevus 1"),
        ("nevus2","Nevus 2"),
        ("normal","Normal"),
        ("intmediate","Intmediate")
    )

    ar_id = models.AutoField(primary_key=True)
    block = models.ForeignKey('blocks.Blocks', on_delete=models.CASCADE, db_column='block', related_name="block_areas")
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    # area = models.CharField(max_length=6, blank=True, null=True)
    # project = models.CharField(max_length=100, blank=True, null=True)
    # old_block_id = models.CharField(max_length=50, blank=True, null=True)
    collection = models.CharField(max_length=2, choices=COLLECTION_CHOICES, default=SCRAPE)
    area_type = models.CharField(max_length=10, choices=AREA_TYPE_TYPES, blank=True, null=True)
    # he_image = models.CharField(max_length=200, blank=True, null=True)
    # na_id = models.CharField(max_length=50, blank=True, null=True)
    completion_date = models.DateField(default=date.today)
    # investigator = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/%y/%m/%d")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'areas'

    def __str__(self):
        return self.name

    def _generate_unique_id(self):
        count = Areas.objects.filter(block=self.block,area_type=self.area_type).count()
        return "%s_%s_%d" % (self.block.name, self.area_type, count + 1)

    def save(self,*args,**kwargs):
        if not self.name:
            self.name = self._generate_unique_id()

        super().save(*args, **kwargs)

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = Areas.objects.all().annotate(num_nucacids=Count('nucacids'))
            if not user.is_superuser:
                return queryset.filter(Q(block__project__technician=user) | Q(block__project__researcher=user))
            return queryset

        def _parse_value(search_value):
            if "_initial:" in search_value:
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "1":"name",
                "2":"block",
                "3":"project",
                "4":"collection",
                "5":"area_type",
                "6":"completion_date",
                "7":"investigator",
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

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if is_initial:
                queryset = queryset.filter(
                        Q(block__bl_id=search_value)
                    )
            elif search_value:
                queryset = queryset.filter(
                        Q(name__icontains=search_value) |
                        Q(block__name__icontains=search_value) |
                        Q(collection__icontains=search_value) |
                        Q(area_type__icontains=search_value) |
                        Q(notes__icontains=search_value)
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
