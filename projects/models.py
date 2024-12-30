from django.db import models
from datetime import datetime
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
import json
from core.validators import validate_name_contains_space

User = get_user_model()

class Project(models.Model):
    BORIS = 'BB'
    IWEI = 'IY'
    AHS = 'AH'
    PI_CHOICES = [
        (BORIS, 'Boris Bastian'),
        (IWEI, 'Iwei Yeh'),
        (AHS, 'Alan Hunter Shain'),
    ]

    name = models.CharField(max_length=100, blank=False, null=False, validators=[validate_name_contains_space], verbose_name="Name")
    abbreviation = models.CharField(max_length=7, blank=False, null=False, unique=True, default='XY', verbose_name="Abbreviation", help_text="Requires a unique identifier for each Project.")
    pi = models.CharField(max_length=2, choices=PI_CHOICES, default=BORIS, blank=True, null=True, verbose_name="Principal Investigator")
    speedtype = models.CharField(max_length=50, blank=True, null=True, verbose_name="Speed Type")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    date_start = models.DateTimeField(blank=True, null=True, default=datetime.now, verbose_name="Start Date")
    technician = models.ManyToManyField(User, null=True, blank=True, related_name="technician_projects", verbose_name="Technician")
    researcher = models.ManyToManyField(User, null=True, blank=True, related_name="researcher_projects", verbose_name="Researcher")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    blocks = models.ManyToManyField('blocks.Block', blank=True, null=True, related_name="block_projects", verbose_name="Blocks")

    class Meta:
        db_table = 'project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
       return self.name

    def query_by_args(self, user, **kwargs):
        def _get_authorizated_queryset():
            queryset = Project.objects.all().annotate(num_blocks=Count('blocks'))
            if not user.is_superuser:
                return queryset.filter(Q(technician=user) | Q(researcher=user))
            return queryset

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
                '0': 'id',
                '1': 'abbreviation',
                '2': 'name',
                '3': 'technician',
                '4': 'researcher',
                '5': 'pi',
                '6': 'date_start',
                '7': 'speedtype',
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            date_range = kwargs.get('date_range', None)[0]
            pi = kwargs.get('pi', None)[0]
            technician = kwargs.get('technician', None)[0]
            researcher = kwargs.get('researcher', None)[0]
            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()
            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)
            if pi:
                queryset = queryset.filter(
                    Q(pi=pi)
                )
            if technician:
                queryset = queryset.filter(
                    Q(technician__id=technician)
                )

            if researcher:
                queryset = queryset.filter(
                    Q(researcher__id=researcher)
                )

            if date_range:
                arr = date_range.split(" to ")
                start_date = datetime.strptime(arr[0],'%Y-%m-%d').date()
                end_date = datetime.strptime(arr[1],'%Y-%m-%d').date()
                queryset = queryset.filter(
                    Q(date_start__gte=start_date) & Q(date_start__lte=end_date)
                )
            if is_initial:
                if search_value["model"] == "area":
                    queryset = queryset.filter(Q(project_blocks__block_areas__id=search_value["id"]))
                if search_value["model"] == "block":
                    queryset = queryset.filter(Q(project_blocks__bl_id=search_value["id"]))
            elif search_value:
                queryset = queryset.filter(
                    Q(id__icontains=search_value) |
                    Q(name__icontains=search_value) |
                    Q(pi__icontains=search_value) |
                    Q(speedtype__icontains=search_value) |
                    Q(abbreviation__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise
