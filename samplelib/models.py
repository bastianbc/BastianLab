from django.db import models
from datetime import date
from django.db.models import Q, Count

class Barcode(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    i5 = models.CharField(max_length=10, unique=True, verbose_name="I5")
    i7 = models.CharField(max_length=10, unique=True, verbose_name="I7")

    class Meta:
        db_table = "barcode"

    def __str__(self):
        return self.name

class SampleLib(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, verbose_name="Barcode")
    date = models.DateField(default=date.today, verbose_name="Date")
    method = models.ForeignKey("method.Method",related_name="sample_libs",on_delete=models.CASCADE, verbose_name="Method")
    qubit = models.FloatField(default=0, verbose_name="Qubit")
    qpcr_conc = models.FloatField(default=0, verbose_name="qPCR Concentration")
    pcr_cycles = models.FloatField(default=0, verbose_name="PCR Cycles")
    amount_in = models.FloatField(default=0, verbose_name="Input Amount")
    amount_final = models.FloatField(default=0, verbose_name="Final Amount")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "sample_lib"

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.vol_remain = self.vol_init
        self.amount_final = self.vol_remain * self.qpcr_conc
        super().save(*args, **kwargs)

    def update_volume(self, volume):
        self.vol_remain = 0 if volume > self.vol_remain else self.vol_remain - volume
        self.save()

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            # queryset = SampleLib.objects.all()
            queryset = SampleLib.objects.all().annotate(num_nucacids=Count('nucacids'))
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
                "2": "barcode",
                "4": "date",
                "5": "method",
                "6": "conc",
                "7": "pcr_cycles",
                "8": "amount_in",
                "9": "amount_final",
                "10": "vol_init",
                "11": "vol_remain",
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
                    Q(name__icontains=search_value)
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

class NA_SL_LINK(models.Model):
    nucacid = models.ForeignKey("libprep.NucAcids",on_delete=models.CASCADE, verbose_name="Nucleic Acid")
    sample_lib = models.ForeignKey(SampleLib, on_delete=models.CASCADE, related_name="nucacids", verbose_name="Sample Library")
    input_vol = models.FloatField(default=0, verbose_name="Te Volume")
    input_amount = models.FloatField(default=0, verbose_name="Input Amount")

    class Meta:
        db_table = "na_sl_link"
