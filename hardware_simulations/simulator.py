import os
import time
import random
import paho.mqtt.client as mqtt

# MQTT configuration from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
PUBLISH_TOPIC = os.getenv('PUBLISH_TOPIC', 'plant/soil_humidity')
PUBLISH_INTERVAL = 5  # seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Simulator connected to MQTT Broker!")
    else:
        print(f"Simulator failed to connect, return code {rc}")

mqtt_client = mqtt.Client()
if MQTT_USERNAME and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqtt_client.on_connect = on_connect

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

try:
    while True:
        humidity = random.uniform(30.0, 70.0)  # Simulated humidity value
        mqtt_client.publish(PUBLISH_TOPIC, humidity)
        print(f"Published humidity: {humidity:.2f}%")
        time.sleep(PUBLISH_INTERVAL)
except KeyboardInterrupt:
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
