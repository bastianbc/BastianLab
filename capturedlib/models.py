from django.db import models
from datetime import date
from django.db.models import Q, Count

class CapturedLib(models.Model):
    BAIT_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    BUFFER_TYPES = (
        ("type1", "Type 1"),
        ("type2", "Type 2"),
        ("type3", "Type 3"),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    barcode = models.ForeignKey("samplelib.Barcode", on_delete=models.CASCADE, verbose_name="Barcode")
    date = models.DateField(default=date.today, verbose_name="Date")
    bait = models.CharField(max_length=20, choices=BAIT_TYPES, verbose_name="Bait", null=True, blank=True)
    frag_size = models.FloatField(default=0, verbose_name="Fragment Size")
    conc = models.FloatField(default=0, verbose_name="Concentration")
    amp_cycle = models.IntegerField(default=0)
    buffer = models.CharField(max_length=20, choices=BUFFER_TYPES, verbose_name="Buffer", null=True, blank=True)
    nm = models.FloatField(default=0, verbose_name="nM")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    pdf = models.FileField(upload_to="uploads/", null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "captured_lib"

    def __str__(self):
        return self.name

    @property
    def amount(self):
        # calculates the amount: amount = vol_init * conc
        result = 0
        try:
            result = self.conc * self.vol_init
        except Exception as e:
            pass

        return result

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = CapturedLib.objects.all()
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
                "3": "date",
                "4": "bait",
                "5": "frag_size",
                "6": "conc",
                "7": "amp_cycle",
                "8": "vol_init",
                "9": "vol_remain",
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

    def set_nm(self):
        # Calculate CL.nM as CL.conc/660 * CL.frag_size * 10^6 and store in CL.nM
        try:
            self.nm = round(self.conc/660 * float(self.frag_size) * 10**6,2)
            self.save()
        except Exception as e:
            print("%s in %s" % (str(e),__file__))
            raise

    def update_volume(self, volume):
        self.vol_remain = 0 if volume > self.vol_remain else self.vol_remain - volume
        self.save()

class SL_CL_LINK(models.Model):
    captured_lib = models.ForeignKey(CapturedLib,on_delete=models.CASCADE, verbose_name="Captured Library", related_name="sl_links")
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, verbose_name="Sample Library", related_name="cl_links")
    volume = models.FloatField(default=0, verbose_name="Volume")

    class Meta:
        db_table = "sl_cl_link"

    @property
    def amount(self):
        # calculates the amount: amount = volume * conc
        result = 0
        try:
            result = self.sample_lib.conc * self.volume
        except Exception as e:
            pass

        return result