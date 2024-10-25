from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *

class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer