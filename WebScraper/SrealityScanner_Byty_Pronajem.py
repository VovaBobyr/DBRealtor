from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
#from mysql.connector import Error
import datetime
#import re
import time
import SrealityLibrary

# Pre-requisites:
# Python:
# mysql-connector-python 8.0.15
# MySQL:
# SET NAMES UTF8MB4
# Connector:
# https://stackoverflow.com/questions/50557234/authentication-plugin-caching-sha2-password-is-not-supported
# auth_plugin='mysql_native_password'

chrome_options = Options()
chrome_options.add_argument("--headless")
#driver = webdriver.Chrome(
#    executable_path='C:/Inst/chromedriver.exe',
#    options=chrome_options)

if os.name == 'nt':
    save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
    chromedriver_path = 'C:/Inst/chromedriver.exe'
else:
    save_path = '/opt/dbrealtor/temp/'
    chromedriver_path = '/usr/bin/chromedriver'

# Count of Advertises on page
adds_on_page = 20
delay = 3

driver = webdriver.Chrome(
    executable_path=chromedriver_path,
    options=chrome_options)

connection_config_dict = {
    'user': 'root',
    'password': SrealityLibrary.take_pass(),
    'host': '127.0.0.1',
    'database': 'dbrealtor',
    'raise_on_warnings': True,
    'use_pure': True,
    'autocommit': True,
    'pool_size': 5
}

script_date_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
type = 'byty_pronajem'
# Define count of all pages based on adds_on_page
adcount = SrealityLibrary.define_pages_count('https://www.sreality.cz/hledani/pronajem/byty', 'byty_pronajem', save_path, driver)
pagescount = int(adcount/adds_on_page) + 1
print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object
counter = 1
# Open Connection and cursor
connection = mysql.connector.connect(**connection_config_dict)
while counter <= pagescount:
    link = 'https://www.sreality.cz/hledani/pronajem/byty?strana=' + str(counter)
    advlist = SrealityLibrary.find_all_links(link, 'pronajem', driver)
    i = 0
    print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Page number: ' + str(counter))
    for advert in advlist:
        i = i + 1
        # Check whether this object already added
        obj_number = advert[advert.rfind('/') + 1:len(advert)]
        is_skipped = SrealityLibrary.find_details_byt_pronajem(advert, i, save_path, type, driver, connection)
        if is_skipped == 'SKIPPED':
            delay = 0
        else:
            delay = 3
        time.sleep(delay)
    counter = counter + 1

SrealityLibrary.final_update_byt_pronajem(type, script_date_start, connection)
connection.close()
driver.close()