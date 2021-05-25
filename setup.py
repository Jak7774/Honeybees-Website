import os
import psycopg2

# global parameters
usb_port = '/dev/ttyACM0' # Arduino Port

#---------- SQL DataBase Details -------
DATABASE_URL = os.environ['DATABASE_URL']
dbConn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = dbConn.cursor()

# ------Query for Web Data
#query = " SELECT a.DateTime, temp1, temp2, temp3, temp4, humid1, humid2 FROM temps as a INNER JOIN humidity as b ON a.DateTime = b.DateTime ORDER BY DateTime "
tempquery  = " SELECT DateTime, temp1, temp2, temp3, temp4 FROM temps ORDER BY DateTime "
humidquery = " SELECT DateTime, humid1, humid2 FROM humidity ORDER BY DateTime "
weightquery = "SELECT DateTime, weight FROM weight ORDER BY DateTime"
