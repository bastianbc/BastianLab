from django.db import models
from django.db.models import Q, Count

class Body(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "body"

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        super().save(*args, **kwargs)

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                "1": "name",
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

            queryset = Body.objects.all()
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
