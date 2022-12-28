from django.db import models
from datetime import date, datetime
from django.db.models import Q, Count

class NucAcids(models.Model):
    DNA = "dna"
    RNA = "rna"
    BOTH = "both"
    NA_TYPES = [
        (DNA, "DNA"),
        (RNA, "RNA"),
        (BOTH, "Both DNA and RNA"),
    ]

    nu_id = models.AutoField(primary_key=True, verbose_name="NA ID")
    area = models.ForeignKey("areas.Areas", on_delete=models.SET_NULL, db_column="area", blank=True, null=True, related_name="nucacids", verbose_name="Area")
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    date = models.DateTimeField(default=datetime.now, verbose_name="Extraction Date")
    method = models.ForeignKey("method.Method",related_name="nuc_acids",on_delete=models.CASCADE, verbose_name="Method")
    na_type = models.CharField(max_length=4, choices=NA_TYPES, verbose_name="NA Type")
    conc = models.FloatField(default=0, verbose_name="Concentration")
    vol_init = models.FloatField(default=0, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(default=0, verbose_name="Volume Remain")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = 'nuc_acids'

    def __str__(self):
        return self.name

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
                "6": "conc",
                "7": "vol_init",
                "8": "vol_remain",
            }

            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            date_range = kwargs.get('date_range', None)[0]
            na_type = kwargs.get('na_type', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if date_range:
                arr = date_range.split(" to ")
                start_date = datetime.strptime(arr[0],'%m/%d/%Y').date()
                end_date = datetime.strptime(arr[1],'%m/%d/%Y').date()
                queryset = queryset.filter(
                    Q(date__gte=start_date) & Q(date__lte=end_date)
                )

            if na_type:
                queryset = queryset.filter(
                    Q(na_type=na_type)
                )

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
        if not self.name:
            na_count = self.area.nucacids.filter(area=self.area,na_type=self.na_type).count() # count of existing nucleic acid
            self.name = "%s-%s-%d" % (self.na_type[0].upper(),self.area.name, na_count + 1)

    def _check_changeability(self):
        if self.sl_links.count() > 0:
            raise Exception("This record cannot be changed as it is used to create SL.")

    def save(self,*args,**kwargs):
        # if not self.name:
        #     self.name = self._generate_unique_name()
        self._generate_unique_name()

        self._check_changeability()

        super().save(*args, **kwargs)

    @property
    def amount(self):
        # calculates the amount: amount = vol_init * conc
        # result = 0
        # try:
        #     result = self.conc * self.vol_init
        # except Exception as e:
        #     pass
        #
        # return result
        return self.conc * self.vol_remain

    def set_init_volume(self):
        self.vol_remain = self.vol_init
        self.save()

    def set_zero_volume(self):
        self.vol_remain = 0.0
        self.save()

    def update_volume(self,amount):
        self.vol_remain -= (amount / self.conc)
        self.save()
