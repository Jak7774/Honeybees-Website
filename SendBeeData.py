#!/usr/bin/python3

import serial
import requests
import datetime

def read_serial():
    data = arduino.readline().decode('utf-8').replace(' ', '')
    data = data.split(',')
    return data

usb_port = '/dev/ttyACM0' # Arduino Port
arduino = serial.Serial(usb_port, 9600)
arduino.flush()   

temp_super, temp_brood, humid_out, temp_out, humid_in, temp_roof, weight = read_serial()
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")

weight = weight.replace('\r\n', '')

jsonData = {  'created_at': now,
    'weight': weight,
    'temp_roof': temp_roof,
    'temp_super_box': temp_super,
    'temp_brood_box': temp_brood,
    'temp_out': temp_out,
    'humid_in': humid_in,
    'humid_out': humid_out}

url ='https://bridgewaterbees.herokuapp.com/hiveData'
response = requests.post(url, json = jsonData)

print("Response:" , response.text)