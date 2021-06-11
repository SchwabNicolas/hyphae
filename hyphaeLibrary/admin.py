from django.contrib import admin

# Register your models here.
from hyphaeLibrary.models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    pass
