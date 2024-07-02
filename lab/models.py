from django.db import models
from django.urls import reverse
from django.db.models import Q, Count
import json
from core.validators import validate_name_contains_space, validate_birthyear_range

class Patients(models.Model):

    RACE_TYPES = (
        (1, "American Indian or Alaska Native"),
        (2, "Asian"),
        (3, "Black or African American"),
        (4, "Native Hawaiian or Other Pacific Islander"),
        (5, "White"),
        (6, "Hispanic/Latino/Spanish Origin (of any race)"),
        (7, "N/A"),
    )

    SEX_TYPES = (
        ("m","Male"),
        ("f","Female"),
    )

    pat_id = models.CharField(max_length=12, blank=False, null=False, unique=True, validators=[validate_name_contains_space], verbose_name="Patient ID", help_text="Requires a unique identifier for each patient.")
    sex = models.CharField(max_length=1, choices=SEX_TYPES, blank=True, null=True, verbose_name="Sex")
    dob = models.PositiveSmallIntegerField(blank=True, null=True, validators=[validate_birthyear_range], verbose_name="Birthyear")
    race = models.SmallIntegerField(choices=RACE_TYPES, default=7, blank=True, null=True)
    source = models.CharField(max_length=20, blank=True, null=True, verbose_name="Source")
    blocks_temp = models.CharField(max_length=100, blank=True, null=True, verbose_name="Blocks")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    pa_id = models.AutoField(primary_key=True)
    pat_ip_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="Intelipath Patient ID", help_text="Requires a unique identifier for each patient from intelipath.")
    date_added = models.DateTimeField(auto_now_add=True)

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

        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'pa_id',
                '1': 'pat_id',
                '2': 'sex',
                '3': 'race',
                '4': 'source',
                '5': 'date_added'
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            race = kwargs.get('race', None)[0]
            sex = kwargs.get('sex', None)[0]
            dob = kwargs.get('dob', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = Patients.objects.all().annotate(num_blocks=Count('patient_blocks'))
            total = queryset.count()
            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)
            if race:
                queryset = queryset.filter(
                    Q(race=race)
                )
            if sex:
                queryset = queryset.filter(
                    Q(sex=sex)
                )
            if dob:
                queryset = queryset.filter(
                    Q(dob=dob)
                )
            if is_initial:
                if search_value["model"] == "block":
                    queryset = queryset.filter(Q(patient_blocks__bl_id=search_value["id"]))
            elif search_value:
                queryset = queryset.filter(
                    Q(pat_id__icontains=search_value) |
                    Q(race__icontains=search_value) |
                    Q(source__icontains=search_value)
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
