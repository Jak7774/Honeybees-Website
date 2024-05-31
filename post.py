#!/usr/bin/env python
import requests
import serial
from datetime import datetime

# Define the USB port for the Arduino
usb_port = '/dev/ttyACM0'

# Initialize serial connection
try:
    arduino = serial.Serial(usb_port, 9600)
    arduino.flush()
except serial.SerialException as e:
    print(f"Error opening serial port {usb_port}: {e}")
    exit()

# Read data from Arduino
try:
    sensor = arduino.readline().decode('utf-8').rstrip()
except Exception as e:
    print(f"Error reading from Arduino: {e}")
    exit()

# Get the current timestamp
dt = datetime.now()
str_dt = dt.strftime("%d/%m/%YT%H:%M:%S")

# Prepare the data dictionary
data = {
    'timestamp': str_dt,
    'values': sensor
}

print("Data to be sent:", data)

# Define the URL of the web server
#url = 'http://localhost:5000/post_endpoint'  # Debug Version
url = 'https://beeserver-94cf5d3aff73.herokuapp.com/post_endpoint'

# Send data to the server
try:
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Data sent successfully!")
    else:
        print("Error:", response.status_code)
except Exception as e:
    print("An error occurred while sending data:", e)


