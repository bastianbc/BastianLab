# from django.db import models
#
# class AuthorizationManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset()\
#             .exclude(user__first_name__exact="")\
#             .exclude(user__last_name__exact="")\
#             .exclude(about__exact="")\
#             .exclude(title__exact="")\
#             .exclude(birth_date__isnull=True)\
#             .exclude(user__avatar='avatars/blank_user.png')
