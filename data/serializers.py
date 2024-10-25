from rest_framework import serializers
from .models import DeviceData


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = ['date', 'time',  'data', 'device_id','timestamp' ]