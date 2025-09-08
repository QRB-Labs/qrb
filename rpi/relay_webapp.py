# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response, jsonify
import RPi.GPIO as GPIO
import socket
import time
import threading
import logging
from logstash import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase
import adafruit_dht
import board


# Setup logging

class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        if isinstance(record.msg, dict):
            message = record.msg
            message.update({
                'path': record.pathname,
                'level': record.levelname,
                'logger_name': record.name,
            })
        else:
            message = {"@message" : record.msg}
        message['@source_host'] = socket.gethostname()
        return self.serialize(message)


mylogger = logging.getLogger(__name__)
handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
handler.setFormatter(LogstashFormatter())
mylogger.addHandler(handler)
mylogger.setLevel(logging.INFO)

app = Flask(__name__)

# GPIO Setup for relay
RELAY_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off initially

# Sensor setup (AM2302 = DHT22, on GPIO 4)
DHT_SENSOR = adafruit_dht.DHT22(board.D4, use_pulseio=False)
DHT_PIN = 4

# Global variable
relay_busy = False

def read_sensor():
    """Read temperature and humidity from AM2302 with retries."""
    for i in range(3):  # Retry up to 3 times
        try:
            temperature = DHT_SENSOR.temperature
            humidity = DHT_SENSOR.humidity
            if humidity is not None and temperature is not None:
                mylogger.info({"message": "Sensor reading",
                               "Temperature": temperature,
                               "Humidity": humidity})
                return round(temperature, 1), round(humidity, 1)
            time.sleep(2)
        except RuntimeError as e:
            mylogger.error(f"Sensor read error (attempt {i+1}): {e}")
            time.sleep(2)
    mylogger.error("Failed to read AM2302 sensor after retries")
    return None, None

def toggle_relay():
    """Run relay for 120 seconds."""
    global relay_busy
    relay_busy = True
    try:
        mylogger.warning("Turning ON")
        print("Turning ON normally-off outlets")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on relay
        time.sleep(120)  # Keep on for 120 seconds
        mylogger.warning("Turning OFF")
        print("Turning OFF normally-off outlets")
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay
    finally:
        relay_busy = False

@app.route('/')
def index():
    temp, hum = read_sensor()
    return render_template('index.html', current_temp=temp, current_hum=hum)

@app.route('/trigger')
def trigger():
    global relay_busy
    if not relay_busy:
        threading.Thread(target=toggle_relay, daemon=True).start()
        return Response("Water is running for 120 seconds!", status=200)
    return Response("Relay is busy, please wait!", status=429)

@app.route('/get_status')
def get_status():
    temp, hum = read_sensor()
    return jsonify({
        'temp': temp,
        'humidity': hum,
        'relay_busy': relay_busy
    })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        GPIO.cleanup()
