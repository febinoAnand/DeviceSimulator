from django.db import models
from django.core.exceptions import ValidationError

class DeviceDetails(models.Model):
    PROTOCOL_CHOICES = [
        ('mqtt', 'MQTT'),
        ('http', 'HTTP')
    ]

    device_name = models.CharField(max_length=45, blank=False)
    device_token = models.CharField(max_length=100, blank=False, unique=True)
    hardware_version = models.CharField(max_length=10, null=True, blank=True)
    software_version = models.CharField(max_length=10, null=True, blank=True)
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)
    protocol = models.CharField(max_length=10, blank=False, choices=PROTOCOL_CHOICES)
    pub_topic = models.CharField(max_length=100, null=True, blank=True)
    sub_topic = models.CharField(max_length=100, null=True, blank=True)
    api_path = models.CharField(max_length=100, null=True, blank=True)
    device_status = models.IntegerField(default=1,null=True,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.device_name

    def clean(self):
      
        if self.protocol == 'mqtt':
            if not self.pub_topic or not self.sub_topic:
                raise ValidationError('pub_topic and sub_topic are required for MQTT protocol.')