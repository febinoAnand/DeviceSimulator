from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework import generics


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    queryset = DeviceDetails.objects.all()
    schema = None
