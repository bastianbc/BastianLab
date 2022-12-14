from django.db import models
from datetime import datetime
from django.db.models import Q, Count

class CapturedLib(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    bait = models.ForeignKey("bait.Bait", verbose_name="Bait", on_delete=models.SET_NULL, null=True, blank=True)
    frag_size = models.FloatField(default=0, verbose_name="Fragment Size")
    conc = models.FloatField(default=0, verbose_name="Concentration")
    amp_cycle = models.IntegerField(default=0)
    buffer = models.ForeignKey("buffer.Buffer", verbose_name="Buffer", on_delete=models.SET_NULL, null=True, blank=True)
    nm = models.FloatField(default=0, verbose_name="nM")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    pdf = models.FileField(upload_to="uploads/", null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "captured_lib"

    def __str__(self):
        return self.name

    __vol_init = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__vol_init = self.vol_init

    def save(self,*args,**kwargs):
        if self.__vol_init != self.vol_init:
            self.vol_remain = self.vol_init

        self._set_nm()

        super().save(*args, **kwargs)

    @property
    def amount(self):
        # calculates the amount: amount = vol_init * conc
        result = 0
        try:
            result = round(self.conc * self.vol_init,2)
        except Exception as e:
            pass

        return result

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = CapturedLib.objects.all().annotate(num_samplelibs=Count('sl_links'))
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
                "0": "id",
                "1": "name",
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

    def _set_nm(self):
        # Calculate CL.nM as CL.conc/660 * CL.frag_size * 10^6 and store in CL.nM
        self.nm = round(self.conc/660 * float(self.frag_size) * 10**6,2)

    def update_volume(self, volume):
        self.vol_remain = 0 if volume > self.vol_remain else round(self.vol_remain - volume,2)
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
            result = self.sample_lib.qpcr_conc * self.volume
        except Exception as e:
            pass

        return result
