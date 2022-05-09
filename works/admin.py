from django.contrib import admin
from works.models import WorkFile, Work, RawWork

admin.site.register(WorkFile)
admin.site.register(RawWork)
admin.site.register(Work)
