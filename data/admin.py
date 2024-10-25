from django.contrib import admin
from .models import DeviceData
from import_export.admin import ExportActionMixin

class DeviceDataAdmin(ExportActionMixin,admin.ModelAdmin):
    list_display = ('date', 'time', 'device_id','data', 'timestamp')
    search_fields = ('device_id__device_token',)
    list_filter = ('date', 'device_id__device_token', 'device_id')

admin.site.register(DeviceData, DeviceDataAdmin)