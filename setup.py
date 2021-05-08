import os
import psycopg2

# global parameters
usb_port = '/dev/ttyACM0' # Arduino Port

#---------- SQL DataBase Details -------
DATABASE_URL = os.environ['DATABASE_URL']
#DATABASE_URL = "postgres://olnhvbxpblxhvh:0aa4b83b313b77dc510803b926619ff2c6e003481c948b795f737ac9202dd4ce@ec2-184-73-198-174.compute-1.amazonaws.com:5432/db6rhe4umj2i5q"
dbConn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = dbConn.cursor()

# ------Query
#query = " SELECT a.DateTime, temp1, temp2, temp3, temp4, humid1, humid2 FROM temps as a INNER JOIN humidity as b ON a.DateTime = b.DateTime ORDER BY DateTime "
tempquery  = " SELECT DateTime, temp1, temp2, temp3, temp4 FROM temps ORDER BY DateTime "
humidquery = " SELECT DateTime, humid1, humid2 FROM humidity ORDER BY DateTime "
