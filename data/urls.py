
from django.urls import path, include
from .views import (
    DeviceDataViewSet, 
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register('devicedata', DeviceDataViewSet)






urlpatterns = [
    path('', include(router.urls)),
]
