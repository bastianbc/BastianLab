from django.db import models
from django.db.models import Q, Count

class Barcodeset(models.Model):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=False)

    class Meta:
        db_table = "barcode_set"

    def __str__(self):
        return self.name

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                "0": "name",
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

            queryset = Barcodeset.objects.all()
            total = queryset.count()

            if search_value:
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

    def activate(self):
        Barcodeset.objects.all().update(active=False)
        self.active = True
        self.save()


class Barcode(models.Model):
    barcode_set = models.ForeignKey("barcodeset.Barcodeset", on_delete=models.CASCADE, related_name="barcodes")
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    i5 = models.CharField(max_length=10, unique=True, verbose_name="I5")
    i7 = models.CharField(max_length=10, unique=True, verbose_name="I7")

    class Meta:
        db_table = "barcode"

    def __str__(self):
        return self.name

    def query_by_args(self, *args, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                "0": "id",
                "1": "name",
                "2": "i5",
                "3": "i7",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]

            barcode_set_id = args[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column


            queryset = Barcode.objects.filter(barcode_set__id=barcode_set_id)
            
            total = queryset.count()

            if search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value),
                    Q(i5__icontains=search_value),
                    Q(i7__icontains=search_value)
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
