import os
import threading
from celery import Celery, shared_task

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Simulator.settings')
django.setup()

from deviceSimulator import simulate_device
from device.models import DeviceDetails


app = Celery('Simulator')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


running_threads = {}

@shared_task
def monitor_device_simulations():
    active_devices = DeviceDetails.objects.filter(is_active=True)
    
    # Start simulation for active devices if not already running
    for device in active_devices:
        if device.device_token not in running_threads:
            thread = threading.Thread(target=simulate_device, args=(device.device_token,))
            running_threads[device.device_token] = thread
            thread.start()
    
    # Stop simulation for inactive devices
    inactive_devices = DeviceDetails.objects.filter(is_active=False)
    for device in inactive_devices:
        if device.device_token in running_threads:
            running_threads[device.device_token].do_run = False
            del running_threads[device.device_token]

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, monitor_device_simulations.s())