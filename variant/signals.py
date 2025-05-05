from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import connection
from variant.models import VariantCall

# def refresh_materialized_view():
#     with connection.cursor() as cursor:
#         cursor.execute("REFRESH MATERIALIZED VIEW variants_view")
#
# @receiver([post_save, post_delete], sender=VariantCall)
# def update_on_variantcall_change(sender, instance, **kwargs):
#     refresh_materialized_view()
