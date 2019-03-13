from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
#import codecs
import mysql.connector
#from mysql.connector import Error
import datetime
import sys
import logging
import time
import SrealityLibrary
from SrealityScanner_Byty_Pronajem_Class import ObjectBytPronajemClass

# Pre-requisites:
# Python:
# mysql-connector-python 8.0.15
# MySQL:
# SET NAMES UTF8MB4
# Connector:
# https://stackoverflow.com/questions/50557234/authentication-plugin-caching-sha2-password-is-not-supported
# auth_plugin='mysql_native_password'

# First imput parameter is Page from what to start load

# Logging
logging.basicConfig(format = u'[%(asctime)s]  %(message)s',filename="../Logs/SrealityScanner_Byty_Pronajem.log", level=logging.INFO)

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

def find_value(search_string, where):
    return_text = ''
    for line in where:
        if search_string in line:
            return_text = line.replace(search_string,'')
            break
    return  return_text

def find_details_byt_pronajem(link, type, driver, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = SrealityLibrary.check_ad_exist(obj_number, type, connection)
    if is_exist:
        logging.info('  Object with number ' + obj_number + ' - SKIPPED')
        #delay=0
        return 'SKIPPED'
    # Title
    driver.get(link)
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            logging.info('  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            logging.error(' 2nd reconnect failed for: ' + link + ' - STOPPING')
            return
    #finally:
    #    connection = mysql.connector.connect(**connection_config_dict)
    #34
    objectbyt = ObjectBytPronajemClass(elems.text.replace('\n',''),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)

    # Description
    elems = driver.find_element_by_class_name('description')
    objectbyt.description = elems.text.replace('\n',' ')

    # Main block with all details (not title and not kontact)
    elems = driver.find_element_by_class_name('params')
    # Processing Params with all details
    all_text = elems.text.split('\n')

    # Celcova cena - if it doesn't exist - find "Zlevněno" and have has to be "Původní cena:"
    insert_text = ''
    insert_text = find_value('Celková cena: ',all_text)
    if insert_text == '':
        insert_text = find_value('cena: ', all_text)
        insert_text = find_value('Zlevněno: ', all_text)
    objectbyt.celkova_cena = insert_text
    # Poznámka k ceně
    insert_text = find_value('Poznámka k ceně: ',all_text)
    objectbyt.poznamka_k_cene = insert_text
    # Cena - define from Celcova cena into Object
    # Check is_cena_digit?
    objectbyt.cena = SrealityLibrary.find_cena(objectbyt.celkova_cena)
    # ID zakázky:
    insert_text = find_value('ID zakázky: ',all_text)
    objectbyt.id_ext = insert_text
    # Aktualizace:
    insert_text = find_value('Aktualizace: ',all_text)
    objectbyt.aktualizace = insert_text
    # Stavba:
    insert_text = find_value('Stavba: ',all_text)
    objectbyt.stavba = insert_text
    # Stav objektu:
    insert_text = find_value('Stav objektu: ',all_text)
    objectbyt.stav_objektu = insert_text
    # Vlastnictví:
    insert_text = find_value('Vlastnictví: ',all_text)
    objectbyt.vlastnictvi = insert_text
    # Umístění objektu:
    insert_text = find_value('Umístění objektu: ',all_text)
    objectbyt.umisteni_objektu = insert_text
    # Podlaží:
    insert_text = find_value('Podlaží: ',all_text)
    objectbyt.podlazi = insert_text
    # Užitná plocha:
    insert_text = find_value('Užitná plocha: ',all_text)
    objectbyt.uzitna_plocha = insert_text
    # Sklep:
    insert_text = find_value('Sklep: ',all_text)
    objectbyt.sklep = insert_text
    # Voda:
    insert_text = find_value('Voda: ',all_text)
    objectbyt.voda = insert_text
    # Odpad:
    insert_text = find_value('Odpad: ',all_text)
    objectbyt.odpad = insert_text
    # Telekomunikace:
    insert_text = find_value('Telekomunikace: ',all_text)
    objectbyt.telekomunikace = insert_text
    # Elektřina:
    insert_text = find_value('Elektřina: ',all_text)
    objectbyt.elektrina = insert_text
    # Doprava:
    insert_text = find_value('Doprava: ',all_text)
    objectbyt.doprava = insert_text
    # Kontakt
    elems = driver.find_element_by_class_name('contacts')
    insert_text = elems.text.split('\n')
    try:
        objectbyt.kontakt = insert_text[0]
        objectbyt.kontakt = insert_text[4]
        objectbyt.kontakt = insert_text[5]
    except:
        pass
    # Zlevneno - if it exist
    insert_text = find_value('Původní cena: ',all_text)
    objectbyt.puvodni_cena = insert_text
    # Link
    objectbyt.link = link
    # Object_Number
    objectbyt.obj_number = link[link.rfind('/') + 1:len(link)]
    # Region and sub-region:
    # it could be that sub-region doesn't exist (exist only for Praha and Brno)
    elems = driver.find_element_by_class_name('regions-box')
    insert_text = elems.text.split('\n')
    if len(insert_text) >=2:
        insert_text[0] = insert_text[0][insert_text[0].find('Pronájem bytů')+14:len(insert_text[0])-1]
        insert_text[1] = insert_text[1][insert_text[1].find('Pronájem bytů')+14:len(insert_text[1])-1]
        objectbyt.region = insert_text[0]
        objectbyt.subregion = insert_text[1]
    if len(insert_text)==1:
        insert_text[0] = insert_text[0][insert_text[0].find('Pronájem bytů ')+14:len(insert_text[0])-1]
        objectbyt.region = insert_text[0]
    #insert_text = elems.text.split('\n')
    #objectbyt.region = insert_text

    # Insert object to DB
    objectbyt.dbinsertbyty()


def final_update_byt_pronajem(type, script_date_start, connection):
    # Input parameter - time of Script start: that to update all rows that are old (were not found now)
    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = 'update dbrealtor.' + type + ' set date_close="' + mydatetime + '", status="C" where date_update < "'\
            + script_date_start + '" OR (date_open < "' + script_date_start + '" AND date_update IS NULL)'
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    row_count = len(cursor.fetchall())
    #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Closed OLD objects count: ', row_count)
    logging.info('  Closed OLD objects count: ', row_count)
    cursor.close()

script_date_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
type = 'byty_pronajem'
# Define count of all pages based on adds_on_page
adcount = SrealityLibrary.define_pages_count('https://www.sreality.cz/hledani/pronajem/byty', driver)
pagescount = int(adcount/adds_on_page) + 1
#print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Pages count: ' + str(pagescount))
logging.info('======================= NEW RUN =======================')
logging.info('  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object

# To have ability load only from defined page
counter = 1
if len(sys.argv) > 1:
    counter = sys.argv[1]
    try:
        counter = int(counter)
    except:
        logging.error('Wrong parameter, not INT')

# Open Connection and cursor
connection = mysql.connector.connect(**connection_config_dict)
while counter <= pagescount:
    link = 'https://www.sreality.cz/hledani/pronajem/byty?strana=' + str(counter)
    advlist = SrealityLibrary.find_all_links(link, 'pronajem', driver)
    i = 0
    #print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Page number: ' + str(counter))
    logging.info('  Page number: ' + str(counter))
    for link in advlist:
        i = i + 1
        # Check whether this object already added
        obj_number = link[link.rfind('/') + 1:len(link)]
        is_skipped = find_details_byt_pronajem(link, type, driver, connection)
        #if is_skipped == 'SKIPPED':
        #    delay = 0
        #else:
        #    delay = 0
        #time.sleep(delay)
    counter = counter + 1

final_update_byt_pronajem(type, script_date_start, connection)
connection.close()
driver.close()