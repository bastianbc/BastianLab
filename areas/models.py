from django.db import models
from django.db.models import Q, Count, Case, When, IntegerField, Value
from datetime import datetime
import json
from core.validators import validate_name_contains_space
from projects.utils import get_user_projects

class Area(models.Model):
    AREA_TYPE_TYPES = [
        ("tumor","Tumor"),
        ("normal","Normal"),
        ("normal1","Normal1"),
        ("normal2","Normal2"),
        ("normal3","Normal3"),
        ("melanoma","Melanoma"),
        ("mel","Mel"),
        ("mel1","Mel1"),
        ("mel2","Mel2"),
        ("mel3","Mel3"),
        ("nevus","Nevus"),
        ("mis","MIS"),
        ("mis1","MIS1"),
        ("mis2","MIS2"),
        ("mis3","MIS3"),
        ("metastasis","Metastasis"),
        ("met","Met"),
        ("met1","Met1"),
        ("met2","Met2"),
        ("met3","Met3"),
        ("ln-met","LN Met"),
        ("ln-met-1","LN Met1"),
        ("ln-met-2","LN Met2"),
        ("ln-met-3","LN Met3"),
        ("invasive-melanoma","Invasive Melanoma"),
        ("cutaneous-metastasis","Cutaneous Metastasis"),
        ("subcutaneous-metastasis","Subcutaneous Metastasis"),
        ("bladder-metastasis","Bladder Metastasis"),
        ("lung-metastasis","Lung Metastasis"),
        ("intestine-metastasis","Intestine Metastasis"),
        ("brain-metastasis","Brain Metastasis"),
        ("skin-metastasis","Skin Metastasis"),
        ("salivary-metastasis","Salivary Metastasis"),
        ("local-recurrent-metastasis","Local Recurrent Metastasis"),
        ("cells","Cells"),
        ("cell-line","Cell Line"),
        ("dn","DN"),
        ("other","Other"),
    ]

    COLLECTION_CHOICES = [
        ('PU', 'Punch'),
        ('SC', 'Scraping'),
        ('PE', 'Cell Pellet'),
        ('CU', 'Curls'),
        ('FF', 'FFPE')
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, validators=[validate_name_contains_space])
    block = models.ForeignKey('blocks.Block', on_delete=models.CASCADE, db_column='block', related_name="block_areas")
    area_type = models.ForeignKey('areatype.AreaType',on_delete=models.CASCADE, db_column='area_type', related_name="areas", null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/%y/%m/%d")
    notes = models.TextField(blank=True, null=True)
    collection = models.CharField(max_length=2, choices=COLLECTION_CHOICES, default="SC")

    class Meta:
        db_table = 'areas'

    def __str__(self):
        return self.name


    def _generate_unique_name(self):
        '''
        Generates unique name for new area. An area belongs to a block. An area's unique name is derived from block name.
        Multiple areas that belong to a block are named incrementally.
        Returns:
            name (str): A string
        '''
        count = Area.objects.filter(block=self.block).count()
        return "%s_area%d" % (self.block.name, count + 1)

    def save(self,*args,**kwargs):
        '''
        Overrides the model's save method.
        '''
        if not self.name:
            self.name = self._generate_unique_name()

        super().save(*args, **kwargs)

    def query_by_args(self, user, **kwargs):
        '''
        This is where the sorting and filtering functions of the datatables are executed.
        Parameters:
            user (obj): Active django user
            kwargs (dict): All parameters that the datatables used
        Returns:
            data (dict): Data that the user will see on the screen
        '''

        def _get_authorizated_queryset():
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''

            queryset = Area.objects.all().annotate(
                num_nucacids=Count('area_na_links', distinct=True),
                num_samplelibs=Count('area_na_links__nucacid__na_sl_links__sample_lib', distinct=True),
                num_blocks=Case(
                    When(block__isnull=False, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                ),
                num_projects=Count(
                    'block__block_projects',
                    distinct=True
                )
            )

            if not user.is_superuser:
                return queryset.filter(block__project=get_user_projects(user))

            return queryset

        def _parse_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                search_value (str): Parsed value
            '''
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
            return search_value

        def _is_initial_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                is_initial (boolean): If there is a initial value, it is True
            '''
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0":"id",
                "1":"name",
                "2":"block",
                "3":"block__project",
                "4":"area_type",
                "5":"completion_date",
                "6":"investigator",
                "7":"num_nucacids",
                "8":"num_samplelibs",
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
                if search_value["model"] == "block":
                    queryset = queryset.filter(Q(block__id=search_value["id"]))
                elif search_value["model"] == "nuc_acid":
                    queryset = queryset.filter(Q(area_na_links__nucacid__id=search_value["id"]))
                elif search_value["model"] == "sample_lib":
                    queryset = queryset.filter(Q(area_na_links__nucacid__na_sl_links__sample_lib__id=search_value["id"]))
                else:
                    queryset = queryset.filter(
                        Q(block__id=search_value) |
                        Q(area_na_links__nucacid__id=search_value)
                    )
            elif search_value:
                queryset = queryset.filter(
                        Q(name__icontains=search_value) |
                        Q(block__name__icontains=search_value) |
                        Q(block__project__name__icontains=search_value) |
                        Q(area_type__value__icontains=search_value) |
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

    @staticmethod
    def get_collections():
        '''
        Option list of Collection for the datatables' select field.
        '''
        return [{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in Area.COLLECTION_CHOICES]

class BLOCK_AREA_LINK(models.Model):
    block = models.ForeignKey("blocks.Block",on_delete=models.CASCADE, related_name="block_area_links", verbose_name="Block")
    area = models.ForeignKey("areas.Area", on_delete=models.CASCADE, related_name="block_area_links", verbose_name="Area")
    input_vol = models.FloatField(blank=True, null=True, verbose_name="Volume")
    input_amount = models.FloatField(blank=True, null=True, verbose_name="Amount")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")

    class Meta:
        db_table = "block_area_link"

    def __str__(self):
        return f"{self.area.name} - {self.nucacid.name}"
