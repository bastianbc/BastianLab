from django.db import models
from datetime import datetime
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

User = get_user_model()

class Projects(models.Model):

    BORIS = 'BB'
    IWEI = 'IY'
    PI_CHOICES = [
        (BORIS, 'Boris Bastian'),
        (IWEI, 'Iwei Yeh'),
    ]
    name = models.CharField(max_length=100, blank=False, null=False,verbose_name="Name")
    abbreviation = models.CharField(max_length=6, blank=False, null=False, unique=True, default='XY', verbose_name="Abbreviation", help_text="Requires a unique identifier for each Project.")
    pi = models.CharField(max_length=2, choices=PI_CHOICES, default=BORIS, blank=True, null=True, verbose_name="Principal Investigator")
    speedtype = models.CharField(max_length=50, blank=True, null=True, verbose_name="Speed Type")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description")
    date_start = models.DateTimeField(blank=True, null=True, default=datetime.now, verbose_name="Start Date")
    pr_id = models.AutoField(primary_key=True, verbose_name="Project ID")
    technician = models.ManyToManyField(User, null=True, related_name="technician_projects", verbose_name="Technician")
    researcher = models.ManyToManyField(User, null=True, related_name="researcher_projects", verbose_name="Researcher")

    class Meta:
        managed = True
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    # def get_absolute_url(self):
    #         return reverse('patient-update', kwargs={'pk': self.pk})

    def __str__(self):
       return self.name

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = Projects.objects.all().annotate(num_blocks=Count('project_blocks'))
            if not user.is_superuser:
                return queryset.filter(Q(technician=user) | Q(researcher=user))
            return queryset

        try:
            ORDER_COLUMN_CHOICES = {
                '1': 'abbreviation',
                '2': 'name',
                '3': 'pi',
                '4': 'date_start',
                '5': 'speedtype',
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

            if search_value:
                queryset = queryset.filter(
                    Q(pr_id__icontains=search_value) |
                    Q(name__icontains=search_value) |
                    Q(pi__icontains=search_value) |
                    Q(speedtype__icontains=search_value)
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
