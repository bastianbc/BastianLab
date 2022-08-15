from django.contrib import admin
from .models import Patients, Blocks, Areas

#Register your models here.
admin.site.register(Patients)
admin.site.register(Blocks)
admin.site.register(Areas)


