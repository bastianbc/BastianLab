from django.db import models
from datetime import date
from django.db.models import Q, Count

class NucAcids(models.Model):
    DNA = "dna"
    RNA = "rna"
    BOTH = "both"
    NA_TYPES = (
        (DNA, "DNA"),
        (RNA, "RNA"),
        (BOTH, "Both DNA and RNA"),
    )

    nu_id = models.AutoField(primary_key=True, verbose_name="NA ID")
    area = models.ForeignKey("areas.Areas", on_delete=models.SET_NULL, db_column="area", blank=True, null=True, related_name="nucacids", verbose_name="Area")
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date = models.DateField(blank=True, null=True, default=date.today, verbose_name="Extraction Date")
    method = models.ForeignKey("method.Method",related_name="nuc_acids",on_delete=models.CASCADE, verbose_name="Method")
    na_type = models.CharField(max_length=4, choices=NA_TYPES, verbose_name="NA Type")
    qubit = models.FloatField(blank=True, null=True, verbose_name="Qubit")
    vol_init = models.FloatField(blank=True, null=True, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(blank=True, null=True, verbose_name="Volume Remain")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = 'nuc_acids'

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            queryset = NucAcids.objects.all()
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
                "2": "area",
                "3": "na_type",
                "4": "date",
                "5": "method",
                "6": "qubit",
                "7": "vol_init",
                "8": "vol_remain",
                "9": "amount",
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
                queryset = queryset.filter(
                        Q(area__ar_id=search_value)
                    )
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(na_type__icontains=search_value) |
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

    def _generate_unique_name(self):
        # blocks.name & Areas.name & first letter of NA_type
        na_count = self.area.nucacids.filter(na_type=self.na_type).count() # count of existing nucleic acid
        return "%s_%s_%s_%d" % (self.area.block.name, self.area.name, self.na_type[0], na_count + 1)

    def save(self,*args,**kwargs):
        if not self.name:
            self.name = self._generate_unique_name()

        self.vol_remain = self.vol_init

        super().save(*args, **kwargs)

    @property
    def amount(self):
        # calculates the amount: amount = vol_init * qubit
        result = 0
        try:
            result = self.qubit * self.vol_init
        except Exception as e:
            pass

        return result

# class SampleLib(models.Model):
#     sl_id = models.CharField(max_length=50, blank=True, null=True)
#     na_id = models.CharField(max_length=50, blank=True, null=True)
#     pre_pcr = models.IntegerField(blank=True, null=True)
#     post_lib_qubit = models.FloatField(blank=True, null=True)
#     post_lib_qpcr = models.FloatField(blank=True, null=True)
#     vol_lib = models.IntegerField(blank=True, null=True)
#     lp_dna = models.FloatField(blank=True, null=True)
#     re_lp_amount = models.FloatField(blank=True, null=True)
#     re_lp2_amount = models.FloatField(blank=True, null=True)
#     total_lp_dna = models.FloatField(blank=True, null=True)
#     chosen_for_capt = models.CharField(max_length=30, blank=True, null=True)
#     input_dna = models.FloatField(blank=True, null=True)
#     input_vol = models.FloatField(blank=True, null=True)
#     post_pcr = models.IntegerField(blank=True, null=True)
#     barcode_id = models.CharField(max_length=50, blank=True, null=True)
#     prep_date = models.DateField(blank=True, null=True)
#     notes = models.CharField(max_length=255, blank=True, null=True)
#     project = models.CharField(max_length=50, blank=True, null=True)
#     nuc_acid = models.ForeignKey(NucAcids, on_delete=models.CASCADE, db_column='nuc_acid', blank=True, null=True)
#
#     class Meta:
#         managed = True
#         db_table = 'sample_lib'
