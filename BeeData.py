#!/usr/bin/env python
import serial
#import MySQLdb
import time
import datetime
from upload_setup import *

temp = []
humid = []
weight = []
    
def read_serial():
    temp.clear() 
    humid.clear()
    weight.clear()
    data = arduino.readline().decode('utf-8').rstrip()
    for i in [0, 1, 3, 5]: # positions of readings
        temp.append(data.split(",")[i])
    for i in [2, 4]:
        humid.append(data.split(",")[i])
    for i in [6]:
        weight.append(data.split(",")[i])
    return temp, humid, weight
    
def inputSQL(temp, humid, weight):
    
    now = datetime.datetime.now()
    date = datetime.date.today()
    time = datetime.datetime.now().strftime("%X")
    
    sql_temp = "insert into temps (datetime, datestamp, timestamp, temp1, temp2, temp3, temp4) values (%s, %s, %s, %s, %s, %s, %s)"
    sql_humid = "insert into humidity (datetime, datestamp, timestamp, humid1, humid2) values (%s, %s, %s, %s, %s)"
    sql_weight = "insert into weight (datetime, datestamp, timestamp, weight) values (%s, %s, %s, %s )"
    
    values_temp = (now, date, time, temp[0], temp[1], temp[2], temp[3])
    values_humid = (now, date, time, humid[0], humid[1])
    values_weight = (now, date, time, weight[0])
    
    cursor.execute(sql_temp, values_temp)
    cursor.execute(sql_humid, values_humid)
    cursor.execute(sql_weight, values_weight)
    dbConn.commit()

arduino = serial.Serial(usb_port, 9600)
arduino.flush()