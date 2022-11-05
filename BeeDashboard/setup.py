import os
import subprocess
import psycopg2
import time
import datetime
import pandas as pd

#---------- SQL DataBase Details -------
db = subprocess.run('/usr/local/bin/heroku config:get DATABASE_URL -a bridgewaterbees',
                              capture_output=True,
                              shell=True)

DATABASE_URL = db.stdout.decode().rstrip() # Strip line breaks and other formatting

dbConn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = dbConn.cursor()

temp = []
humid = []
weight = []

def readSQL():
    
    #date = datetime.date.today()
    date = datetime.datetime.strptime('2022-02-27', '%Y-%m-%d')
    last7 = (date - datetime.timedelta(days=7)).date()
    str_last7 = "'" + str(last7) + "'"
    time = datetime.datetime.now().strftime("%X")

    tempquery  = " SELECT DateTime, temp1, temp2, temp3, temp4 FROM temps WHERE datestamp >= " + str_last7 + " ORDER BY DateTime "
    humidquery = " SELECT DateTime, humid1, humid2 FROM humidity WHERE datestamp >= " + str_last7 + " ORDER BY DateTime "
    weightquery = "SELECT DateTime, weight FROM weight WHERE datestamp >= " + str_last7 + " ORDER BY DateTime "

    temp = pd.read_sql(tempquery, con=dbConn)
    humid = pd.read_sql(humidquery, con=dbConn)
    weight = pd.read_sql(weightquery, con=dbConn)
    return temp, humid, weight
