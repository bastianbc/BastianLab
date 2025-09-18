from django.db import models
from datetime import datetime
from django.db.models import Q, Count, Sum
from core.validators import validate_name_contains_space
from sequencinglib.models import CL_SEQL_LINK
import json
from projects.utils import get_user_projects

class CapturedLib(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[validate_name_contains_space], verbose_name="Name")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    bait = models.ForeignKey("bait.Bait", verbose_name="Bait", on_delete=models.SET_NULL, null=True, blank=True, related_name="captured_libs")
    frag_size = models.FloatField(default=0, verbose_name="Fragment Size")
    conc = models.FloatField(default=0, verbose_name="Concentration")
    amp_cycle = models.IntegerField(default=0)
    buffer = models.ForeignKey("buffer.Buffer", verbose_name="Buffer", on_delete=models.SET_NULL, null=True, blank=True)
    nm = models.FloatField(default=0, verbose_name="nM")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    pdf = models.FileField(upload_to="uploads/captured_lib_pdf_attachments", null=True, blank=True)
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
        if self.pk:
            if self.__vol_init != self.vol_init:
                self.vol_remain = self.vol_init

            self._set_nm()

        super().save(*args, **kwargs)

    @property
    def amount(self):
        # calculates the amount: sum of all amounts that link belongs to self
        result = sum(link.amount for link in SL_CL_LINK.objects.filter(captured_lib=self))
        return round(result, 2) if result is not None else 0


    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''
            queryset = CapturedLib.objects.all().annotate(
                num_samplelibs=Count('sl_cl_links', distinct=True),
                num_sequencinglibs=Count('cl_seql_links',distinct=True)
            )

            if not user.is_superuser:
                return queryset.filter(
                    sl_cl_links__sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

            return queryset

        def _parse_value(search_value):
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
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
            normal_area = kwargs.get('normal_area', None)[0]
            bait_filter = kwargs.get('bait', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if is_initial:
                if search_value["model"] == "sample_lib":
                    filter = [sl_cl_link.captured_lib.id for sl_cl_link in SL_CL_LINK.objects.filter(sample_lib__id=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
                if search_value["model"] == "seqlib":
                    filter = [cl_seql_link.captured_lib.id for cl_seql_link in
                              CL_SEQL_LINK.objects.filter(sequencing_lib__id=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(date__icontains=search_value)
                )

            if normal_area:
                 queryset = queryset.filter(
                    Q(sl_cl_links__sample_lib__na_sl_links__nucacid__na_type='dna') &
                    Q(sl_cl_links__sample_lib__na_sl_links__nucacid__area_na_links__area__area_type__value='normal')
            )
            if bait_filter:
                queryset = queryset.filter(
                    Q(bait=bait_filter)
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
        if not self.frag_size or self.frag_size == 0:
            return
        self.nm = round(self.conc/(660 * float(self.frag_size)) * 10**6,2)



    def update_volume(self, volume):
        self.vol_remain = 0 if volume > self.vol_remain else round(self.vol_remain - volume,2)
        self.save()

class SL_CL_LINK(models.Model):
    captured_lib = models.ForeignKey("capturedlib.CapturedLib",on_delete=models.CASCADE, verbose_name="Captured Library", related_name="sl_cl_links")
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, verbose_name="Sample Library", related_name="sl_cl_links")
    volume = models.FloatField(default=0, verbose_name="Volume")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")

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
