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

        try:
            ORDER_COLUMN_CHOICES = {
                "1": "nu_id",
                "2": "area",
                "3": "block",
                "4": "na_type",
                "5": "date_extr",
                "6": "method",
                "7": "qubit",
                "8": "volume",
                "9": "amount",
                "10": "re_ext",
                "11": "total_ext",
                "12": "na_sheared",
                "13": "shearing_vol",
                "14": "te_vol",
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
                    Q(nu_id__icontains=search_value) |
                    Q(area__ar_id__icontains=search_value) |
                    Q(na_type__icontains=search_value) |
                    Q(na_type__icontains=search_value) |
                    Q(method__icontains=search_value) |
                    Q(date_extr__icontains=search_value)
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
        na_count = self.area.nucacids.count() # count of existing nucleic acid
        return "%s_%s_%s_%d" % (self.area.block.name, self.area.name, self.na_type[0], na_count + 1)

    def save(self,*args,**kwargs):
        if not self.name:
            self.name = self._generate_unique_name()
            print("self.name:",self.name)

        super().save(*args, **kwargs)

    # @property
    # def calc_amount(self):
    #     # calculates the amount
    #     return self.qubit * self.volume
    # def save(self, *args, **kwargs):
    #     #Following lines set qubit and volume to 0 if they are None.
    #     kwargs.get('qubit',0)
    #     kwargs.get('volume',0)
    #     self.amount = self.qubit * self.volume
    #     super(NucAcids, self).save(*args, **kwargs)

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
