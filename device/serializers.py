from rest_framework import serializers
from .models import *


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetails
        fields = ('id','device_name','hardware_version','software_version','device_token','protocol','pub_topic','sub_topic','api_path', 'device_status', 'is_active')