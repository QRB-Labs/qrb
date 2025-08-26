from flask import Flask, render_template, Response
import RPi.GPIO as GPIO
import time
import threading
from logstash import TCPLogstashHandler
import logging

mylogger =  logging.getLogger(__name__)
handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
mylogger.addHandler(handler)

app = Flask(__name__)

# Set GPIO numbering mode to BCM
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 16
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Ensure relay is off initially

# Global variable to prevent concurrent relay triggers
relay_busy = False

def toggle_relay():
    global relay_busy
    relay_busy = True
    try:
        print("Turning ON normally-off outlets")
        mylogger.warning("Turning ON")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on relay
        time.sleep(120)  # Keep on for 120 seconds
        print("Turning OFF normally-off outlets")
        mylogger.warning("Turning OFF")
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay
    finally:
        relay_busy = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trigger')
def trigger():
    global relay_busy
    if not relay_busy:
        threading.Thread(target=toggle_relay, daemon=True).start()
        return Response("Water is running for 120 seconds!", status=200)
    return Response("Relay is busy, please wait!", status=429)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        GPIO.cleanup()
