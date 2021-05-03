import serial
import MySQLdb

# global parameters
usb_port = '/dev/ttyACM0' # Arduino Port

#---------- SQL DataBase Details -------
dbConn = MySQLdb.connect(host='localhost',
                         user='phpmyadmin',
                         passwd='H0n3yb33s',
                         db='phpmyadmin') or die ('Could not connect to Database')

cursor = dbConn.cursor()

# ------Query
#query = " SELECT a.DateTime, temp1, temp2, temp3, temp4, humid1, humid2 FROM temps as a INNER JOIN humidity as b ON a.DateTime = b.DateTime ORDER BY DateTime "
tempquery  = " SELECT DateTime, temp1, temp2, temp3, temp4 FROM temps ORDER BY DateTime "
humidquery = " SELECT DateTime, humid1, humid2 FROM humidity ORDER BY DateTime "
