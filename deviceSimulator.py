import paho.mqtt.client as mqtt
import json
import time
import threading
import random
from datetime import datetime, timedelta


MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

publish_topic = "pub_topic"
device_token = "dev"

running_threads = {}

base_payload = {
    "device_token": device_token,
    "M001": 0.0000, "M002": 0.0000, "M003": 0.0000, "shift_no": 1.0000,
    "M004": 0.0000, "M005": 0.0000, "M006": 0.0000, "M007": 0.0000, "M008": 0.0000,
    "M009": 0.0000, "M010": 0.0000, "M011": 0.0000, "M012": 0.0000, 
    "M013": 0.0000, "M014": 0.0000, "M015": 0.0000, "M016": 0.0000,
    "M017": 0.0000, "M018": 0.0000, "PD": 3.0000, "PM": 10.0000, "PY": 2024.0000,
    "PHR": 18.0000, "PMIN": 36.0000, "PSEC": 29.0000, "SHIFTRST": 0.0000, 
    "timestamp": 1727960724
}


incremental_step = {
    "M001": 10.0, "M002": 4.0, "M003": 5.0, "M004": 15.0, "M005": 20.0,
    "M006": 30.0, "M007": 8.0, "M008": 6.0, "M009": 1.0, "M010": 3.0,
    "M011": 4.0, "M012": 11.0, "M013": 15.0, "M014": 9.0, "M015": 7.0,
    "M016": 16.0, "M017": 13.0, "M018": 5.0
}


def update_shift_no_and_reset_if_needed(payload, previous_shift_no):
    current_time = datetime.now()
    
    
    shift_1_start = current_time.replace(hour=6, minute=30, second=0, microsecond=0)
    shift_2_start = current_time.replace(hour=2, minute=30, second=0, microsecond=0)
    shift_3_start = current_time.replace(hour=10, minute=30, second=0, microsecond=0)
    shift_3_end = (shift_1_start + timedelta(days=1)).replace(hour=6, minute=29, second=59, microsecond=0)

    new_shift_no = payload["shift_no"]

    if shift_1_start <= current_time < shift_2_start or current_time < shift_1_start:
        new_shift_no = 1.000
    elif shift_2_start <= current_time < shift_3_start:
        new_shift_no = 2.000
    elif shift_3_start <= current_time or current_time < shift_1_start:
        new_shift_no = 3.000

    
    if new_shift_no != previous_shift_no:
        for key in [f"M{str(i).zfill(3)}" for i in range(1, 19)]:
            payload[key] = 0.0000

    payload["shift_no"] = new_shift_no
    return payload


def update_date_time_fields(payload):
    current_time = datetime.now()
    payload["PD"] = float(current_time.day)  
    payload["PM"] = float(current_time.month)  
    payload["PY"] = float(current_time.year)  
    payload["PHR"] = float(current_time.hour)  
    payload["PMIN"] = float(current_time.minute)  
    payload["PSEC"] = float(current_time.second)  
    return payload


def simulate_device(device_id):
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Device {device_id} connected successfully")
        else:
            print(f"Device {device_id} failed to connect, return code {rc}")

    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    current_payload = base_payload.copy()
    current_payload["device_token"] = device_token
    previous_shift_no = current_payload["shift_no"]
    last_increment_time = time.time()

    threading.current_thread().do_run = True
    while getattr(threading.current_thread(), "do_run", True):
        current_time = time.time()
        if current_time - last_increment_time >= 30:
            for key in incremental_step:
                current_payload[key] = round(current_payload[key] + incremental_step[key], 3)
            last_increment_time = current_time

        current_payload["timestamp"] = int(time.time())
        current_payload = update_date_time_fields(current_payload)
        current_payload = update_shift_no_and_reset_if_needed(current_payload, previous_shift_no)
        previous_shift_no = current_payload["shift_no"]

        json_payload = json.dumps(current_payload)
        client.publish(publish_topic, json_payload)
        print(f"Device {device_id} sent data: {json_payload}")

        time.sleep(1)
    
    client.loop_stop()
    client.disconnect()
    print(f"Device {device_id} simulation stopped.")


def simulate_multiple_devices(device_count=100):
    threads = []
    for device_id in range(1, device_count + 1):
        thread = threading.Thread(target=simulate_device, args=(device_id,))
        threads.append(thread)
        thread.start()


    for thread in threads:
        thread.join()


if __name__ == "__main__":
    simulate_multiple_devices(1)
