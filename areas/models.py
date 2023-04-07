from django.db import models
from django.db.models import Q, Count
from datetime import datetime
from django.utils.crypto import get_random_string

class Areas(models.Model):
    AREA_TYPE_TYPES = [
        ("normal","Normal"),
        ("normal2","Normal1"),
        ("normal3","Normal2"),
        ("melanoma","Melanoma"),
        ("mel1","Mel1"),
        ("mel2","Mel2"),
        ("mel3","Mel3"),
        ("nevus","Nevus"),
        ("mis","MIS"),
        ("mis1","MIS1"),
        ("mis2","MIS2"),
        ("mis3","MIS3"),
        ("metastasis","Metastasis"),
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
        ("other","Other"),
    ]

    ar_id = models.AutoField(primary_key=True)
    block = models.ForeignKey('blocks.Blocks', on_delete=models.CASCADE, db_column='block', related_name="block_areas")
    name = models.CharField(max_length=50, unique=True)
    area_type = models.CharField(max_length=30, choices=AREA_TYPE_TYPES, blank=True, null=True)
    completion_date = models.DateTimeField(default=datetime.now)
    image = models.ImageField(null=True, blank=True, upload_to="images/%y/%m/%d")
    notes = models.TextField(blank=True, null=True)

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
        count = Areas.objects.filter(block=self.block).count()
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
            queryset = Areas.objects.all().annotate(num_nucacids=Count('nucacids'))
            if not user.is_superuser:
                return queryset.filter(Q(block__project__technician=user) | Q(block__project__researcher=user))
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
                v = search_value.split("_initial:")[1]
                return None if v == "null" or not v.isnumeric() else v
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
                "0":"ar_id",
                "1":"name",
                "2":"block",
                "3":"block__project",
                "4":"area_type",
                "5":"completion_date",
                "6":"investigator",
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

    @staticmethod
    def get_area_types():
        '''
        Option list of Area Type for the datatables' select field.
        '''
        return [{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in Areas.AREA_TYPE_TYPES]
