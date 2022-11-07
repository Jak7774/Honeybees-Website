#!/usr/bin/env python

from setup import *
#from upload_setup import *
from datetime import datetime
#import MySQLdb
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px

tempquery  = " SELECT DateTime, temp1, temp2, temp3, temp4 FROM temps ORDER BY DateTime "
humidquery = " SELECT DateTime, humid1, humid2 FROM humidity ORDER BY DateTime "
weightquery = "SELECT DateTime, weight FROM weight ORDER BY DateTime"


x = datetime.now() # Current DateTime for Reference

#---------------------------------------
# Temperature Setup
#---------------------------------------

rdgs = pd.read_sql(tempquery, con=dbConn)

#-------- Data Tidy Up
error_fields = []

def replace_value(value, field):
    global error_fields
    if value < -15 or value > 100:
        if field not in error_fields:
            error_fields.append(field)
        return None
    else:
        return value
  
for field in ['temp1', 'temp2', 'temp3', 'temp4']:
    rdgs[field] = rdgs.apply(lambda row: replace_value(row[field], field), axis=1)
    
rdgs_plt = pd.melt(rdgs, id_vars=['datetime'], var_name='tempsensor', value_name='reading')
rdgs_plt['daydiff'] = (x - rdgs_plt['datetime']) / np.timedelta64(1, 'D')

rdgs_plt.loc[rdgs_plt['daydiff'] <= 1, 'daygrp'] = 1
rdgs_plt.loc[(rdgs_plt['daydiff'] > 1) & (rdgs_plt['daydiff'] <= 7) , 'daygrp'] = 2
rdgs_plt.loc[(rdgs_plt['daydiff'] > 7) & (rdgs_plt['daydiff'] <= 30) , 'daygrp'] = 3
rdgs_plt.loc[(rdgs_plt['daydiff'] > 30) & (rdgs_plt['daydiff'] <= 90) , 'daygrp'] = 4
rdgs_plt.loc[(rdgs_plt['daydiff'] > 90) & (rdgs_plt['daydiff'] <= 180) , 'daygrp'] = 5
rdgs_plt.loc[(rdgs_plt['daydiff'] > 180) & (rdgs_plt['daydiff'] <= 365) , 'daygrp'] = 6
rdgs_plt.loc[rdgs_plt['daydiff'] > 365 , 'daygrp'] = 7

rdgs_plt.loc[rdgs_plt['daygrp'] == 1, 'daygrp_lab'] = "1 Day"
rdgs_plt.loc[rdgs_plt['daygrp'] == 2, 'daygrp_lab'] = "1 Week"
rdgs_plt.loc[rdgs_plt['daygrp'] == 3, 'daygrp_lab'] = "1 Month"
rdgs_plt.loc[rdgs_plt['daygrp'] == 4, 'daygrp_lab'] = "3 Months"
rdgs_plt.loc[rdgs_plt['daygrp'] == 5, 'daygrp_lab'] = "6 Months"
rdgs_plt.loc[rdgs_plt['daygrp'] == 6, 'daygrp_lab'] = "12 Months"
rdgs_plt.loc[rdgs_plt['daygrp'] == 7, 'daygrp_lab'] = "Older still"

# rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp1', 'sensor_label'] = "Super"
rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp1', 'sensor_label'] = "Outside"
rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp2', 'sensor_label'] = "Brood"
# rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp3', 'sensor_label'] = "Outside"
rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp3', 'sensor_label'] = "Super"
# rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp4', 'sensor_label'] = "Roof"
rdgs_plt.loc[rdgs_plt['tempsensor'] == 'temp4', 'sensor_label'] = "Outside (Dual)"


# Create the Timegroups
timegrp = rdgs_plt.daygrp.unique()
timegrp_lab = rdgs_plt.daygrp_lab.unique()

#---------------------------------------
# Humidity Setup
#---------------------------------------

humid = pd.read_sql(humidquery, con=dbConn)

humid_plt = pd.melt(humid, id_vars=['datetime'], var_name='humidsensor', value_name='reading')

humid_plt['daydiff'] = (x - humid_plt['datetime']) / np.timedelta64(1, 'D')
humid_plt.loc[humid_plt['daydiff'] <= 1, 'daygrp'] = 1
humid_plt.loc[(humid_plt['daydiff'] > 1) & (humid_plt['daydiff'] <= 7) , 'daygrp'] = 2
humid_plt.loc[(humid_plt['daydiff'] > 7) & (humid_plt['daydiff'] <= 30) , 'daygrp'] = 3
humid_plt.loc[(humid_plt['daydiff'] > 30) & (humid_plt['daydiff'] <= 90) , 'daygrp'] = 4
humid_plt.loc[(humid_plt['daydiff'] > 90) & (humid_plt['daydiff'] <= 180) , 'daygrp'] = 5
humid_plt.loc[(humid_plt['daydiff'] > 180) & (humid_plt['daydiff'] <= 365) , 'daygrp'] = 6
humid_plt.loc[humid_plt['daydiff'] > 365 , 'daygrp'] = 7

humid_plt.loc[humid_plt['daygrp'] == 1, 'daygrp_lab'] = "1 Day"
humid_plt.loc[humid_plt['daygrp'] == 2, 'daygrp_lab'] = "1 Week"
humid_plt.loc[humid_plt['daygrp'] == 3, 'daygrp_lab'] = "1 Month"
humid_plt.loc[humid_plt['daygrp'] == 4, 'daygrp_lab'] = "3 Months"
humid_plt.loc[humid_plt['daygrp'] == 5, 'daygrp_lab'] = "6 Months"
humid_plt.loc[humid_plt['daygrp'] == 6, 'daygrp_lab'] = "12 Months"
humid_plt.loc[humid_plt['daygrp'] == 7, 'daygrp_lab'] = "Older still"

# humid_plt.loc[humid_plt['humidsensor'] == 'humid1', 'sensor_label'] = "Outside"
humid_plt.loc[humid_plt['humidsensor'] == 'humid1', 'sensor_label'] = "Super"
# humid_plt.loc[humid_plt['humidsensor'] == 'humid2', 'sensor_label'] = "Roof"
humid_plt.loc[humid_plt['humidsensor'] == 'humid2', 'sensor_label'] = "Outside"

humid_timegrp = humid_plt.daygrp.unique()
humid_timegrp_lab = humid_plt.daygrp_lab.unique()

#---------------------------------------
# Weight Setup
#---------------------------------------

weight = pd.read_sql(weightquery, con=dbConn)
weight_plt = pd.melt(weight, id_vars=['datetime'], var_name='weightsensor', value_name='reading')

weight_plt['daydiff'] = (x - weight_plt['datetime']) / np.timedelta64(1, 'D')
weight_plt.loc[weight_plt['daydiff'] <= 1, 'daygrp'] = 1
weight_plt.loc[(weight_plt['daydiff'] > 1) & (weight_plt['daydiff'] <= 7) , 'daygrp'] = 2
weight_plt.loc[(weight_plt['daydiff'] > 7) & (weight_plt['daydiff'] <= 30) , 'daygrp'] = 3
weight_plt.loc[(weight_plt['daydiff'] > 30) & (weight_plt['daydiff'] <= 90) , 'daygrp'] = 4
weight_plt.loc[(weight_plt['daydiff'] > 90) & (weight_plt['daydiff'] <= 180) , 'daygrp'] = 5
weight_plt.loc[(weight_plt['daydiff'] > 180) & (weight_plt['daydiff'] <= 365) , 'daygrp'] = 6
weight_plt.loc[weight_plt['daydiff'] > 365 , 'daygrp'] = 7

weight_plt.loc[weight_plt['daygrp'] == 1, 'daygrp_lab'] = "1 Day"
weight_plt.loc[weight_plt['daygrp'] == 2, 'daygrp_lab'] = "1 Week"
weight_plt.loc[weight_plt['daygrp'] == 3, 'daygrp_lab'] = "1 Month"
weight_plt.loc[weight_plt['daygrp'] == 4, 'daygrp_lab'] = "3 Months"
weight_plt.loc[weight_plt['daygrp'] == 5, 'daygrp_lab'] = "6 Months"
weight_plt.loc[weight_plt['daygrp'] == 6, 'daygrp_lab'] = "12 Months"
weight_plt.loc[weight_plt['daygrp'] == 7, 'daygrp_lab'] = "Older still"

weight_timegrp = weight_plt.daygrp.unique()
weight_timegrp_lab = weight_plt.daygrp_lab.unique()
