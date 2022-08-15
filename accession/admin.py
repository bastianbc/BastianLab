from django.contrib import admin
from .models import IpPatients,Accessions,Parts,Melanomas,Outcomes

# Register your models here.
admin.site.register(IpPatients)
admin.site.register(Parts)
admin.site.register(Melanomas)
admin.site.register(Outcomes)
admin.site.register(Accessions)