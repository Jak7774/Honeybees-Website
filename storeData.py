#!/usr/bin/env python
import serial
import csv
from datetime import datetime

usb_port = '/dev/ttyACM0'
arduino = serial.Serial(usb_port, 9600)
arduino.flush()

data = arduino.readline().decode('utf-8').rstrip()
dt = datetime.now()
str_dt = dt.strftime("%m/%d/%YT%H:%M:%S")

res = []
res.append(str_dt)
res.append(data)

print(res)

with open('/home/pi/Data.csv','a') as fd:
    writer = csv.writer(fd)
    writer.writerow(res)

