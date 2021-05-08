#!/usr/bin/env python

import time
from upload_setup import *
from BeeData import *


hive_temp, hive_humid = read_serial()
inputSQL(hive_temp, hive_humid)
