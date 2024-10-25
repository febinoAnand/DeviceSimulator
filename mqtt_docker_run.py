import os
import django
import paho.mqtt.client as mqtt
import json
import datetime
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Simulator.settings')
django.setup()

from data.models import DeviceData
from device.models import DeviceDetails
from django.db.models.signals import post_save
from django.dispatch import receiver

BUILT_IN_TOPICS = [
    'sub_topic',
    'pub_topic'
]

subscribed_topics = set()
enable_printing = False

def on_connect(client, userdata, flags, rc):
    global enable_printing

    if rc == 0:
        if enable_printing:
            print('Connected successfully')

        global subscribed_topics
        for topic in BUILT_IN_TOPICS:
            if topic not in subscribed_topics:
                client.subscribe(topic)
                subscribed_topics.add(topic)
                if enable_printing:
                    print(f'Subscribed to {topic}')
        if enable_printing:
            print("All built-in topics are successfully subscribed!")
    else:
        if enable_printing:
            print(f'Bad connection. Code: {rc}')

@receiver(post_save, sender=DeviceDetails)
def handle_device_details_save(sender, instance, **kwargs):
    if instance.sub_topic: 
        subscribe_to_topic(instance.sub_topic)

def subscribe_to_topic(sub_topic):
    global enable_printing

    if sub_topic not in subscribed_topics:
        mqtt_client.subscribe(sub_topic)
        subscribed_topics.add(sub_topic)
        if enable_printing:
            print(f'Subscribed to {sub_topic}')
    else:
        if enable_printing: 
            print(f'Topic {sub_topic} is already subscribed.')

def publish_response(mqtt_client, device_token, response, is_error=False):
    global enable_printing
    try:
        publish_topic = 'pub_topic'
        result = mqtt_client.publish(publish_topic + '/' + device_token, json.dumps(response))
        if enable_printing:
            print(f"Response Published to {publish_topic}: {response}")
    except Exception as e:
        if enable_printing:
            print(f"An error occurred: {e}")

def log_message(currentMessage, topic, protocol='MQTT', response=None):
    global enable_printing
    try:
        message_data = json.loads(currentMessage)
        data_id = str(message_data['timestamp']) if 'timestamp' in message_data else None
    except json.JSONDecodeError:
        message_data = None
        data_id = None

    return message_data

def on_message(mqtt_client, userdata, msg):
    try:
        print()
        print()
        print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
        currentMessage = msg.payload.decode()

        message_data = log_message(currentMessage, msg.topic)

        if message_data is None:
            response = {
                "status": "INVALID JSON",
                "message": "The received message is not a valid JSON",
                "timestamp": int(datetime.datetime.now().timestamp())
            }
            publish_response(mqtt_client, '', response, is_error=True)
            return

        device_token = message_data.get('device_token', '')
        timestamp = message_data.get('timestamp', int(datetime.datetime.now().timestamp()))

        if 'cmd' in message_data and message_data['cmd'] == "TIMESTAMP" and device_token:
            handle_command_message(mqtt_client, msg, message_data)
        elif 'timestamp' in message_data and device_token and 'shift_no' in message_data:
            handle_machine_data(mqtt_client, msg, message_data)
        else:
            response = {
                "status": "UNKNOWN FORMAT",
                "message": "Received message format is not recognized",
                "timestamp": timestamp
            }
            publish_response(mqtt_client, device_token, response, is_error=True)
    except Exception as e:
        print(e)

def handle_command_message(mqtt_client, msg, message_data):
    global enable_printing

    current_timestamp = int(datetime.datetime.now().timestamp())
    device_token = message_data['device_token']

    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        if enable_printing:
            print("device", device)
        device_data = DeviceData(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            data=message_data,
            device_id=device,
        )
        device_data.save()
        if enable_printing:
            print(f'Saved device data to database: {device_data}')

        response = {
            "status": "OK",
            "device_token": device_token,
            "cmd_response": current_timestamp,
        }
        publish_response(mqtt_client, device_token, response)

    except DeviceDetails.DoesNotExist:
        response = {
            "status": "DEVICE NOT FOUND",
            "message": "Device not found with given token"
        }
        publish_response(mqtt_client, device_token, response, is_error=True)
        if enable_printing:
            print('Device token mismatch')

def handle_machine_data(mqtt_client, msg, message_data):
    global enable_printing
    timestamp = message_data['timestamp']
    device_token = message_data.get('device_token', '')
    errors = []

    if all(k in message_data for k in ('PHR', 'PMIN', 'PSEC', 'PD', 'PM', 'PY')):
        plcHR = int(message_data['PHR'])
        plcMIN = int(message_data['PMIN'])
        plcSEC = int(message_data['PSEC'])
        plcDate = int(message_data['PD'])
        plcMonth = int(message_data['PM'])
        plcYear = int(message_data['PY'])

        message_date = datetime.date(plcYear, plcMonth, plcDate)
        message_time = datetime.time(plcHR, plcMIN, plcSEC)
    else:
        errors.append({
            "status": "INVALID TIMESTAMP - PHR",
            "message": "PHR PMIN PSEC Time Stamp Not Received",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
            print('PHR PMIN PSEC Time Stamp Not Received')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        if enable_printing:
            print("device", device)
    except DeviceDetails.DoesNotExist:
        errors.append({
            "status": "DEVICE NOT FOUND",
            "message": "Device not found with given token",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
            print('Device token mismatch')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    deviceFirstData = DeviceData.objects.filter(device_id__device_token=device_token).order_by('data__timestamp').first()

    if deviceFirstData and "timestamp" in deviceFirstData.data:
        oldTimestamp = deviceFirstData.data["timestamp"]
        if oldTimestamp > timestamp:
            errors.append({
                "status": "INVALID TIMESTAMP",
                "message": "Received timestamp is less than first data timestamp",
                "device_token": device_token,
                "timestamp": timestamp
            })
            if enable_printing:
                print('Received timestamp is less than current timestamp: firstTimestamp =', oldTimestamp, '- Received =', timestamp)
            publish_response(mqtt_client, device_token, errors, is_error=True)
            return False
    else:
        if enable_printing:
            print('No previous data found. Saving this as the first data entry for device_token:', device_token)

    currentTimestamp = time.time()
    if currentTimestamp < timestamp:
        errors.append({
            "status": "INVALID TIMESTAMP",
            "message": "Received timestamp is greater than current timestamp",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
            print('Received timestamp is greater than current timestamp current =', currentTimestamp, ' - Received', timestamp)
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    if DeviceData.objects.filter(timestamp=str(timestamp), device_id__device_token=device_token).exists(): 
        errors.append({
            "status": "DUPLICATE TIMESTAMP",
            "message": "Duplicate timestamp found, data not saved.",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
            print('Duplicate timestamp found, data not saved.')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    device_data = DeviceData(
        date=message_date,
        time=message_time,
        data=message_data,
        device_id=device,
        timestamp=str(timestamp),
    )
    device_data.save()

    response = {
        "status": "OK",
        "message": "Successfully saved data",
        "device_token": device_token,
        "timestamp": timestamp
    }
    publish_response(mqtt_client, device_token, response)
    
    if enable_printing:
        print(f'Saved device data to database: {device_data}')
    
    return True

mqtt_client = mqtt.Client()
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_DELAY = 5

def on_disconnect(client, userdata, rc):
    global enable_printing

    if rc != 0:
        if enable_printing:
            print("Unexpected disconnection.")
        attempt_reconnect(client)

def attempt_reconnect(client):
    global enable_printing

    for attempt in range(MAX_RECONNECT_ATTEMPTS):
        if enable_printing:
            print(f"Attempting to reconnect ({attempt + 1}/{MAX_RECONNECT_ATTEMPTS})...")
        time.sleep(RECONNECT_DELAY)
        try:
            client.reconnect()
            if enable_printing:
                print("Reconnected successfully!")
            break
        except Exception as e:
            if enable_printing:
                print(f"Reconnection attempt failed: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

mqtt_client.connect("broker.emqx.io", 1883, 60)

while True:
    try:
        mqtt_client.loop_start()
        time.sleep(1)
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        break
