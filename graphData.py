#!/usr/bin/env python

from setup import *
from datetime import datetime
import MySQLdb
import pandas as pd
import numpy as np
import plotly.express as px

x = datetime.now() # Current DateTime for Reference

#---------------------------------------
# Temperature Setup
#---------------------------------------

rdgs = pd.read_sql(tempquery, con=dbConn)

rdgs_plt = pd.melt(rdgs, id_vars=['DateTime'], var_name='TempSensor', value_name='Reading')
rdgs_plt['daydiff'] = (x - rdgs_plt['DateTime']) / np.timedelta64(1, 'D')
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

timegrp = rdgs_plt.daygrp.unique()
timegrp_lab = rdgs_plt.daygrp_lab.unique()

#---------------------------------------
# Humidity Setup
#---------------------------------------

humid = pd.read_sql(humidquery, con=dbConn)

humid_plt = pd.melt(humid, id_vars=['DateTime'], var_name='HumidSensor', value_name='Reading')

humid_plt['daydiff'] = (x - humid_plt['DateTime']) / np.timedelta64(1, 'D')
humid_plt.loc[humid_plt['daydiff'] <= 1, 'daygrp'] = 1
humid_plt.loc[(rdgs_plt['daydiff'] > 1) & (humid_plt['daydiff'] <= 7) , 'daygrp'] = 2
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

humid_timegrp = humid_plt.daygrp.unique()
humid_timegrp_lab = humid_plt.daygrp_lab.unique()

