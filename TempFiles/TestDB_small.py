import mysql.connector
from mysql.connector import Error
import datetime

def take_pass():
    filename = 'c:/inst/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

connection_config_dict = {
    'host': '127.0.0.1',
    'database': 'dbrealtor',
    'user': 'root',
    'password': 'mysql#root_Fragout_12345'
}

def quotes(str):
    return "'" + str + "'"

def values(objlist):
    longstr = ""
    for str in objlist:
        longstr = longstr + quotes(str) + ","
    return longstr[0:len(longstr)-1]
try:
    mydb = mysql.connector.connect(host='127.0.0.1',database='dbrealtor',user='root',password="mysql#root_Fragout_12345")

    objlist = ('1', '2')
    my1 = "'1'"
    my2 = "'2'"
    query = """INSERT INTO byty (title,typ_bytu) VALUES('2','2')"""
    cursor = mydb.cursor()
    mylist = ("1","2")
    cursor.execute(query, mylist)
    mydb.commit()
    print(cursor.rowcount, "record inserted.")
    mydb.close()

except Error as e:
    print('Error:', e)
