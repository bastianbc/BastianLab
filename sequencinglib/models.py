from django.db import models
from datetime import date
from django.db.models import Q, Count

class SequencingLib(models.Model):
    BUFFER_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date = models.DateField(default=date.today, verbose_name="Date")
    nmol = models.FloatField(default=0, verbose_name="N Mol")
    buffer = models.CharField(max_length=20, choices=BUFFER_TYPES, verbose_name="Buffer")
    pdf = models.FileField(upload_to="uploads/")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "sequencing_lib"

    def __str__(self):
        return self.name

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = SequencingLib.objects.all()
            if not user.is_superuser:
                return queryset.filter(Q(area__block__project__technician=user) | Q(area__block__project__researcher=user))
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
                "1": "name",
                "2": "date",
                "3": "nmol",
                "4": "buffer",
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
                    Q(name__icontains=search_value) |
                    Q(date__icontains=search_value)
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

class CL_SEQL_LINK(models.Model):
    sequencing_lib = models.ForeignKey(SequencingLib,on_delete=models.CASCADE, verbose_name="Sequencing Library")
    captured_lib = models.ForeignKey("capturedlib.CapturedLib", on_delete=models.CASCADE, verbose_name="Captured Library")
    volume = models.FloatField(default=0, verbose_name="Volume")

    class Meta:
        db_table = "cl_seql_link"

    @property
    def persentage(self):
        # calculates the amount: amount = volume * conc
        return 0
