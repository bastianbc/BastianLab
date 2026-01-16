from django.db.models import FloatField
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


# -------------------------------------------------------------------
# Model Utilities
# -------------------------------------------------------------------

def custom_update(model, pk, parameters):
    """
    Generic update helper for Django models.

    - Casts FloatFields safely
    - Resolves ForeignKey relations automatically
    - Ignores 'pk' in parameters
    """

    try:
        obj = model.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return None

    for key, value in parameters.items():
        if key == "pk":
            continue

        field = obj._meta.get_field(key)

        # Float casting
        if isinstance(field, FloatField) and value is not None:
            value = float(value)

        # ForeignKey resolution
        if field.is_relation and field.related_model and value is not None:
            value = field.related_model.objects.get(pk=value)

        setattr(obj, key, value)

    obj.save()
    return obj


# # -------------------------------------------------------------------
# # Email Service
# # -------------------------------------------------------------------
#
# class MailService:
#     """
#     Central email service abstraction.
#     """
#
#     @staticmethod
#     def send(
#         *,
#         subject: str,
#         body: str,
#         to: list[str],
#         html: str | None = None,
#         cc: list[str] | None = None,
#         bcc: list[str] | None = None,
#     ) -> None:
#         msg = EmailMessage(
#             subject=subject,
#             body=html or body,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=to,
#             cc=cc or [],
#             bcc=bcc or [],
#         )
#
#         if html:
#             msg.content_subtype = "html"
#
#         msg.send(fail_silently=False)
#
#
# # -------------------------------------------------------------------
# # SMTP Health Check
# # -------------------------------------------------------------------
#
# def smtp_health(request):
#     """
#     Lightweight SMTP connectivity health check.
#     """
#
#     try:
#         conn = get_connection()
#         conn.open()
#         conn.close()
#         MailService.send(
#             subject="Pipeline Completed",
#             body="Variant ingestion completed successfully.",
#             to=["ceylan.bagci@ucsf.edu"],
#         )
#         return JsonResponse(
#             {
#                 "smtp": "ok",
#                 "backend": settings.EMAIL_BACKEND,
#                 "host": settings.EMAIL_HOST,
#                 "port": settings.EMAIL_PORT,
#             }
#         )
#
#     except Exception as e:
#         return JsonResponse(
#             {
#                 "smtp": "error",
#                 "detail": str(e),
#             },
#             status=500,
#         )
