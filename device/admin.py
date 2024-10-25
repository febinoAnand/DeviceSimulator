from django.contrib import admin
from .models import *

class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_token', 'hardware_version', 'software_version', 'protocol', 'create_date_time', 'is_active')
    search_fields = ('device_name', 'device_token', 'protocol')
    list_filter = ('device_name', 'device_token', 'protocol', 'create_date_time')


admin.site.register(DeviceDetails, DeviceDetailsAdmin)
