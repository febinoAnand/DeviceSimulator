import datetime as datetime
from django.utils import timezone,dateformat
import datetime
from django.db import models
from device.models import DeviceDetails
from datetime import timedelta

    

class DeviceData(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    data = models.JSONField(blank=False)
    device_id = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)
    timestamp=models.CharField(max_length=50, unique=False, blank=False,null=True)

    def __str__(self):
        return str(self.device_id.device_name)
