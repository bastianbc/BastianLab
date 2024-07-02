from django.db import models
from datetime import datetime
from django.db.models import Q, Count, OuterRef, Subquery, Value
import json
from core.validators import validate_name_contains_space
from capturedlib.models import SL_CL_LINK

class SampleLib(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[validate_name_contains_space], verbose_name="Name")
    barcode = models.ForeignKey("barcodeset.Barcode", blank=True, null=True, on_delete=models.CASCADE, verbose_name="Barcode")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
    method = models.ForeignKey("method.Method",related_name="sample_libs",on_delete=models.CASCADE, blank=True, null=True, verbose_name="Method")
    qubit = models.FloatField(default=0, verbose_name="Qubit")
    shear_volume = models.FloatField(default=0, verbose_name="Shear Volume")
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

    __vol_init = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__vol_init = self.vol_init

    def save(self,*args,**kwargs):
        if self.__vol_init != self.vol_init:
            self.vol_remain = self.vol_init
            self.amount_final = self.vol_remain * self.qpcr_conc
        self.vol_remain = round(self.vol_remain, 2)
        super().save(*args, **kwargs)

    def update_volume(self, volume):
        self.vol_remain = 0 if volume > self.vol_remain else self.vol_remain - volume
        self.save()

    def update_qpcr(self, value):
        self.qpcr_conc = value
        self.save()

    @staticmethod
    def query_by_args(user, **kwargs):

        def _get_authorizated_queryset():

            return SampleLib.objects.all().annotate(
                num_nucacids=Count('na_sl_links',distinct=True),
                num_files=Count('sequencing_file_sets__sequencing_files',distinct=True),
                num_blocks=Count('na_sl_links', distinct=True),
                num_capturedlibs=Count('sl_cl_links', distinct=True),
                area_num=Count("na_sl_links__nucacid__area_na_links__area", distinct=True),
            )

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
                "2": "barcode",
                "3": "date",
                "4": "num_files",
                "5": "qpcr_conc",
                "6": "vol_init",
                "7": "amount_final",
                "8": "pcr_cycles",
                "9": "qubit",
                "10": "amount_in",
                "11": "vol_remain",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            sequencing_run_filter = kwargs.get('sequencing_run', None)[0]
            # patient_filter = kwargs.get('patient', None)[0]
            barcode_filter = kwargs.get('barcode', None)[0]
            i5_filter = kwargs.get('i5', None)[0]
            i7_filter = kwargs.get('i7', None)[0]
            area_type_filter = kwargs.get('area_type', None)[0]
            bait_filter = kwargs.get('bait', None)[0]
            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)
            print("search_value:", "$" * 100)
            print(search_value)
            if sequencing_run_filter:
                from sequencingrun.models import SequencingRun

                filter = []
                try:
                    seq_r = SequencingRun.objects.get(id=sequencing_run_filter)
                    for seq_l in seq_r.sequencing_libs.all():
                        for cl_seql_link in seq_l.cl_seql_links.all():
                            for sl_cl_link in cl_seql_link.captured_lib.sl_cl_links.all():
                                filter.append(sl_cl_link.sample_lib.name)

                except Exception as e:
                    pass

                queryset = queryset.filter(Q(name__in=filter))

            # if patient_filter:
            #     filter = [na_sl_link.sample_lib.name for na_sl_link in NA_SL_LINK.objects.filter(nucacid__area__block__patient__pat_id=patient_filter)]
            #     queryset = queryset.filter(Q(name__in=filter))

            if barcode_filter:
                queryset = queryset.filter(Q(barcode__id=barcode_filter))

            if i5_filter:
                queryset = queryset.filter(Q(barcode__i5=i5_filter))

            if i7_filter:
                queryset = queryset.filter(Q(barcode__i7=i7_filter))

            if area_type_filter:
                if area_type_filter == "normal":
                    filter = [na_sl_link.sample_lib.name for na_sl_link in NA_SL_LINK.objects.filter(nucacid__area__area_type=area_type_filter)]
                else:
                    filter = [na_sl_link.sample_lib.name for na_sl_link in NA_SL_LINK.objects.exclude(nucacid__area__area_type="normal")]

                queryset = queryset.filter(Q(name__in=filter))

            if bait_filter:
                from capturedlib.models import CapturedLib

                filter = []
                try:
                    for captured_lib in CapturedLib.objects.filter(bait=bait_filter):
                        for sl_cl_link in captured_lib.sl_cl_links.all():
                            filter.append(sl_cl_link.sample_lib.name)

                except Exception as e:
                    pass

                queryset = queryset.filter(Q(name__in=filter))
            print("search_value:", "*"*100)
            print(search_value)
            if is_initial:
                if search_value["model"] == "nucacid":
                    filter = [na_sl_link.sample_lib.id for na_sl_link in NA_SL_LINK.objects.filter(nucacid=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
                if search_value["model"] == "area":
                    filter = [na_sl_link.sample_lib.id for na_sl_link in NA_SL_LINK.objects.filter(nucacid__area_na_links__area=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
                if search_value["model"] == "captured_lib":
                    filter = [sl_cl_link.sample_lib.id for sl_cl_link in
                              SL_CL_LINK.objects.filter(captured_lib__id=search_value["id"])]
                    queryset = queryset.filter(Q(id__in=filter))
                    print(queryset)
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value)
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

class NA_SL_LINK(models.Model):
    nucacid = models.ForeignKey("libprep.NucAcids",on_delete=models.CASCADE, related_name="na_sl_links", verbose_name="Nucleic Acid")
    sample_lib = models.ForeignKey(SampleLib, on_delete=models.CASCADE, related_name="na_sl_links", verbose_name="Sample Library")
    input_vol = models.FloatField(default=0, verbose_name="Te Volume")
    input_amount = models.FloatField(default=0, verbose_name="Input Amount")
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")


    class Meta:
        db_table = "na_sl_link"
