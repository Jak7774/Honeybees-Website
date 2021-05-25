import os
import subprocess
import psycopg2

# global parameters
usb_port = '/dev/ttyACM0' # Arduino Port

#---------- SQL DataBase Details -------
db = subprocess.run('/usr/local/bin/heroku config:get DATABASE_URL -a bridgewaterbees',
                              capture_output=True,
                              shell=True)

DATABASE_URL = db.stdout.decode().rstrip() # Strip line breaks and other formatting

dbConn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = dbConn.cursor()
