from django.db import models
from datetime import datetime
from django.db.models import Q
from django.db.models import Count, Subquery, OuterRef, Value
from django.db.models.functions import Coalesce
from samplelib.models import NA_SL_LINK
import json
from core.validators import validate_name_contains_space
from projects.utils import get_user_projects

class NucAcids(models.Model):
    DNA = "dna"
    RNA = "rna"
    BOTH = "both"
    NA_TYPES = [
        (DNA, "DNA"),
        (RNA, "RNA"),
        (BOTH, "Both DNA and RNA"),
    ]

    name = models.CharField(max_length=50, unique=True, validators=[validate_name_contains_space], verbose_name="Name")
    date = models.DateTimeField(default=datetime.now, verbose_name="Extraction Date")
    method = models.ForeignKey("method.Method",related_name="nuc_acids",on_delete=models.CASCADE, blank=True, null=True, verbose_name="Method")
    na_type = models.CharField(max_length=4, choices=NA_TYPES, blank=True, null=True, verbose_name="NA Type")
    conc = models.FloatField(default=0, verbose_name="Concentration")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = 'nuc_acids'

    def __str__(self):
        return self.name

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
            queryset = NucAcids.objects.all().annotate(
                num_areas=Count('area_na_links__area', distinct=True),
                num_samplelibs=Coalesce(Subquery(
                    NA_SL_LINK.objects.filter(
                        nucacid=OuterRef("pk")
                    ).values("nucacid").annotate(
                        cnt=Count("sample_lib", distinct=True)
                    ).values("cnt")[:1],  # Limit to 1 to ensure correct subquery usage
                ), Value(0))
            )
            if not user.is_superuser:
                return queryset.filter(
                    area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

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
                "0": "id",
                "1": "name",
                "2": "num_areas",
                "3": "na_type",
                "4": "date",
                "5": "method",
                "6": "conc",
                "7": "vol_init",
                "8": "vol_remain",
                "10": "num_samplelibs",
            }

            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            date_range = kwargs.get('date_range', None)[0]
            na_type = kwargs.get('na_type', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()
            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)
            if date_range:
                arr = date_range.split(" to ")
                start_date = datetime.strptime(arr[0],'%Y-%m-%d').date()
                end_date = datetime.strptime(arr[1],'%Y-%m-%d').date()
                queryset = queryset.filter(
                    Q(date__gte=start_date) & Q(date__lte=end_date)
                )

            if na_type:
                queryset = queryset.filter(
                    Q(na_type=na_type)
                )

            if is_initial:
                if search_value["model"] == "area":
                    queryset = queryset.filter(Q(area_na_links__area__id=search_value["id"]))
                elif search_value["model"] == "sample_lib":
                    queryset = queryset.filter(Q(na_sl_links__sample_lib__id=search_value["id"]))
                else:
                    queryset = queryset.filter(
                            Q(area_na_links__area__id=search_value)
                        )
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(na_type__icontains=search_value) |
                    Q(area_na_links__area__name__icontains=search_value)|
                    Q(na_sl_links__sample_lib__name__icontains=search_value)
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


    def _set_init_volume(self):
        '''
        Sets vol_remain to vol_init during changing another values if not used to create SL.
        '''
        if self.na_sl_links.count() < 1:
            self.vol_remain = self.vol_init

    def _check_changeability(self):
        '''
        Checks that allow only the remaining volume to be changed after the SL is created. If there is a rule violation throws an exception.
        '''
        if self.id and self.na_sl_links.count() > 0:
            existing_na = NucAcids.objects.get(id=self.id)
            if not self.conc == existing_na.conc or not self.vol_init == existing_na.vol_init:
                raise Exception("This record cannot be changed as it is used to create SL.")

    def save(self,*args,**kwargs):
        '''
        Overrides the model's save method.
        '''
        if self.pk:
            self._check_changeability()

            self._set_init_volume()

        super().save(*args, **kwargs)

    @property
    def amount(self):
        '''
        Calculates the amount that vol_init * conc
        '''
        return self.conc * self.vol_remain

    def update_volume(self,amount):
        '''
        Updates the volume. If this nucleic acid is used to create a sample library, the remaining volume is recalculated and saved.
        Parameters:
            amount (float): A float number
        '''
        self.vol_remain = round(self.vol_remain - (amount / self.conc),2)
        self.save()


class AREA_NA_LINK(models.Model):
    nucacid = models.ForeignKey("libprep.NucAcids",on_delete=models.CASCADE, related_name="area_na_links", verbose_name="Nucleic Acid")
    area = models.ForeignKey("areas.Area", on_delete=models.CASCADE, related_name="area_na_links", verbose_name="Area")
    input_vol = models.FloatField(blank=True, null=True, verbose_name="Volume")
    input_amount = models.FloatField(blank=True, null=True, verbose_name="Amount")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")

    class Meta:
        db_table = "area_na_link"

    def __str__(self):
        return f"{self.area.name} - {self.nucacid.name}"
