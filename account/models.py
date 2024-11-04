from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class User(User):

    class Meta:
        proxy = True

    def __unicode__(self):
        return self.get_full_name()

    @property
    def full_name(self):
        return self.get_full_name()

    def query_by_args(self, **kwargs):
        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'username',
                '1': 'first_name',
                '2': 'last_name',
                '4': 'last_login',
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

            queryset = User.objects.filter(is_superuser=False)
            total = queryset.count()

            if search_value:
                queryset = queryset.filter(
                    Q(username__icontains=search_value) |
                    Q(first_name__icontains=search_value) |
                    Q(last_name__icontains=search_value)
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

    def reset_password(self):
        self.last_login = None
        self.save()
