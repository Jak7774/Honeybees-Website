#!/usr/bin/env python

import time
from setup import *
from BeeData import *
from graphData import *
from WebServer import *

def updateBees():
    if arduino.in_waiting > 0:
            hive_temp, hive_humid = read_serial()
            print(hive_temp, hive_humid)
            inputSQL(hive_temp, hive_humid)
            time.sleep(300) # Every 5 Mins

app.run_server(debug=False, host='0.0.0.0', port=8050)

while True:
    updateBees()

#if __name__=="__main__":
#    main()
