from django.db import models
from django.contrib.auth.models import User
import json

class AnalysisRun(models.Model):
    PIPELINE_CHOICES = (
        ("v1", "V1"),
    )

    GENOME_CHOICES = (
        ("hg19", "Hg19"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analysis_runs")
    name = models.CharField(max_length=12, unique=True, verbose_name="Name")
    pipeline = models.CharField(max_length=10, choices=PIPELINE_CHOICES, verbose_name = "Pipeline Version")
    genome = models.CharField(max_length=10, choices=GENOME_CHOICES, verbose_name = "Reference Genome")
    date = models.DateTimeField(auto_now_add=True)
    sheet = models.FileField(upload_to="files/")

    class Meta:
        db_table = "analysis_run"

    def generate_name(self):
        last_run = AnalysisRun.objects.all().order_by('id').last()
        if last_run:
            last_id = int(last_run.name.replace('AR', ''))
            return f"AR{last_id + 1:04d}"
        else:
            return "AR1"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_name()
        super(AnalysisRun, self).save(*args, **kwargs)

    def query_by_args(self, user, **kwargs):
        def _get_authorizated_queryset():
            return AnalysisRun.objects.all()

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
                "2": "pipeline",
                "3": "genome",
                "4": "date",
                "5": "sheet",
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
                pass
            elif search_value:
                queryset = queryset.filter(
                    Q(pipeline__icontains=search_value) |
                    Q(date__icontains=search_value) |
                    Q(genome__icontains=search_value)
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