#!/usr/bin/python3

import time
from upload_setup import *
from BeeData import *

hive_temp, hive_humid, hive_weight = read_serial()
inputSQL(hive_temp, hive_humid, hive_weight)