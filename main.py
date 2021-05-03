#!/usr/bin/env python

import time
from setup import *
from BeeData import *

while True:
    if arduino.in_waiting > 0:
        hive_temp, hive_humid = read_serial()
        print(hive_temp, hive_humid)
        inputSQL(hive_temp, hive_humid)
        time.sleep(300) # Every 5 Mins
            
            
if __name__=="__main__":
    main()