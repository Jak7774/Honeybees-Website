#!/usr/bin/env python
import serial
import MySQLdb
import time
import datetime
from setup import *

temp = []
humid = []
    
def read_serial():
    temp.clear() 
    humid.clear()
    data = arduino.readline().decode('utf-8').rstrip()
    for i in [0, 1, 3, 5]: # positions of temp readings
        temp.append(data.split(",")[i])
    for i in [2, 4]:
        humid.append(data.split(",")[i])
    return temp, humid
    
def inputSQL(temp, humid):
    
    now = datetime.datetime.now()
    date = datetime.date.today()
    time = datetime.datetime.now().strftime("%X")
    
    sql_temp = "insert into temps (DateTime, DateStamp, TimeStamp, temp1, temp2, temp3, temp4) values (%s, %s, %s, %s, %s, %s, %s)"
    sql_humid = "insert into humidity (DateTime, DateStamp, TimeStamp, humid1, humid2) values (%s, %s, %s, %s, %s)"
    
    values_temp = (now, date, time, temp[0], temp[1], temp[2], temp[3])
    values_humid = (now, date, time, humid[0], humid[1])
    
    cursor.execute(sql_temp, values_temp)
    cursor.execute(sql_humid, values_humid)
    dbConn.commit()

arduino = serial.Serial(usb_port, 9600, timeout=1)
arduino.flush()
# read_serial()
# inputSQL(temp, humid)
