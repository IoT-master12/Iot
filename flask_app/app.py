import os
from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import paho.mqtt.client as mqtt
import datetime

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soil_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class SoilData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    humidity = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# MQTT configuration from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_TOPIC = "plant/soil_humidity"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    with app.app_context():  # Push the application context
        try:
            humidity = float(msg.payload.decode())
            data = SoilData(timestamp=datetime.datetime.utcnow(), humidity=humidity)
            db.session.add(data)
            db.session.commit()
            print(f"Received and stored humidity: {humidity}%")
        except ValueError:
            print("Received invalid humidity data")
        except Exception as e:
            print(f"Error storing humidity data: {e}")


mqtt_client = mqtt.Client()
if MQTT_USERNAME and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# API endpoints
@app.route('/data', methods=['GET'])
def get_data():
    data = SoilData.query.order_by(SoilData.timestamp.desc()).limit(100).all()
    result = [
        {"timestamp": d.timestamp.isoformat(), "humidity": d.humidity} for d in data
    ]
    return jsonify(result)

# Serve the mobile client HTML
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
