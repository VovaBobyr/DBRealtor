'''
 Script for test environment:
 1. Check chromedriver
 2. Check that HTML files is saved
 3. Check connection to DB (mySQL)
'''
import codecs

import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime

PROJECT_PATH_LINUX = '/opt/dbrealtor/'
PROJECT_PATH_WIN = 'c:/inst/'

def save_page(page_name, save_path, driver, link):
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    driver.get(link)
    html = driver.page_source
    file_object.write(html)
    file_object.close()

def test_webdirver():
    if os.name == 'nt':
        save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
        chromedriver_path = 'C:/Inst/chromedriver.exe'
    else:
        save_path = '/opt/dbrealtor/temp/'
        chromedriver_path = '/usr/bin/chromedriver'
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            executable_path=chromedriver_path,
            options=chrome_options)

        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   OPENED 1st Driver')

        link ='https://www.sreality.cz/detail/prodej/byt/1+kk/cerhovice--/2535706204'
        driver.get(link)
        driver.close()
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   WebDriver - OK!')
    except:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   WebDriver - FAIL!')

def take_pass():
    if os.name == 'nt':
        filename = PROJECT_PATH_WIN + 'info.txt'
    else:
        filename = PROJECT_PATH_LINUX + 'Backups/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

def test_dbconnection():
    connection_config_dict = {
        'user': 'vlad',
        'password': take_pass(),
        'host': '127.0.0.1',
        # 'host': '3.125.96.243',
        'database': 'dbrealtor',
        'raise_on_warnings': True,
        #'use_pure': True,
        'autocommit': True,
        'pool_size': 5,
         'auth_plugin': 'mysql_native_password'
    }
    #connection = mysql.connector.connect(**connection_config_dict)
    '''connection = mysql.connector.connect(
                                #user='vlad',
                                #password='vlad_#Katrin123',
                                user='vlad',
                                password=take_pass(),
                                host='127.0.0.1',
                                database='dbrealtor',
                                auth_plugin='mysql_native_password')'''
    connection = mysql.connector.connect(**connection_config_dict)

    query = 'SELECT * FROM dbrealtor.dataloadlog LIMIT 1'
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute(query)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   Result is: ' + str(cursor.rowcount))
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   DB connection - OK!')
    except:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   DB connection - FAIL!')
    finally:
        cursor.close()

#test_webdirver()
test_dbconnection()
pass