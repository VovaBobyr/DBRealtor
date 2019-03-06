import mysql.connector
from mysql.connector import Error

def take_pass():
    filename = 'c:/inst/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

connection_config_dict = {
    'user': 'root',
    'password': take_pass(),
    'host': '127.0.0.1',
    'database': 'dbrealtor',
    'raise_on_warnings': True,
    'use_pure': True,
    'autocommit': True,
    'pool_size': 5
}


connection = mysql.connector.connect(**connection_config_dict)

mycursor = connection.cursor()
# query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
sql1 = "SELECT link FROM dbrealtor.byty"
mycursor.execute(sql1)

myresult = mycursor.fetchall()
i=0
for x in myresult:
    i = i + 1
    obj_number = x[0][x[0].rfind('/') + 1:len(x[0])]
    sql2 = 'update dbrealtor.byty set obj_number=' + obj_number + ' where link="' + x[0] + '"'
    mycursor2 = connection.cursor()
    mycursor2.execute(sql2)
    #if i/10 == 0:
    print('Count:  ' + str(i))
    connection.commit()


mycursor.close()
connection.close()
