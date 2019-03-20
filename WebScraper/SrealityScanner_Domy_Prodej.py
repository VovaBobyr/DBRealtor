from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
import datetime
import time
import sys
import logging
import SrealityLibrary
from SrealityScanner_Domy_Prodej_Class import ObjectDomyProdejClass

# First imput parameter is Page from what to start load

# Logging
script_date_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

chrome_options = Options()
chrome_options.add_argument("--headless")

if os.name == 'nt':
    is_win = True
else:
    is_win = False

if is_win:
    save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
    chromedriver_path = 'C:/Inst/chromedriver.exe'
    log_name = 'C:/Learning/Python/DBRealtor/Logs/SrealityScanner_Domy_Prodej_' + script_date_start[:10] + '.log'
else:
    save_path = '/opt/dbrealtor/temp/'
    chromedriver_path = '/usr/bin/chromedriver'
    log_name = '/opt/dbrealtor/Logs/SrealityScanner_Domy_Prodej_'+ script_date_start[:10] +'.log'

logging.basicConfig(format = u'[%(asctime)s]  %(message)s',filename=log_name, level=logging.INFO)

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

# Big part to find details in HTML
def find_details_byt_prodej(link, type, id_load, driver, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = SrealityLibrary.check_ad_exist(obj_number, type, connection)
    if is_exist:
        logging.info('  Object with number ' + obj_number + ' - SKIPPED')
        #delay=0
        return 'Skipped'
    # Title
    driver.get(link)
    #print('Driver GET - Find all details.')
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            logging.info('  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            logging.info(' 2nd reconnect failed for: ' + link + ' - STOPPING')
            return 'Failed'
    #finally:
    #    connection = mysql.connector.connect(**connection_config_dict)
    #38
    objectbyt = ObjectDomyProdejClass('','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)
    #Title
    objectbyt.title = elems.text.replace('\n', '')
    # id_load
    objectbyt.id_load = str(id_load)
    # Description
    elems = driver.find_element_by_class_name('description')
    descr_text = elems.text.replace('\n',' ')
    descr_text = descr_text.replace("'","")
    objectbyt.description = descr_text

    # Main block with all details (not title and not kontakt)
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
    # Cena - define from Celcova cana into Object
    # Check is_cena_digit?
    objectbyt.cena = SrealityLibrary.find_cena(objectbyt.celkova_cena)
    # Náklady na bydlení::
    insert_text = find_value('Náklady na bydlení: ',all_text)
    objectbyt.naklady = insert_text
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
    # Typ domu:
    insert_text = find_value('Typ domu: ',all_text)
    objectbyt.umisteni_objektu = insert_text
    # Podlaží:
    insert_text = find_value('Podlaží: ',all_text)
    objectbyt.podlazi = insert_text
    # Podlaží:
    insert_text = find_value('Počet bytu: ',all_text)
    objectbyt.pocet_bytu = insert_text
    # Užitná plocha:
    insert_text = find_value('Užitná plocha: ',all_text)
    objectbyt.uzitna_plocha = insert_text
    # Plocha podlahová:
    insert_text = find_value('Plocha podlahová: ',all_text)
    objectbyt.uzitna_plocha = insert_text
    # Poloha domu::
    insert_text = find_value('Poloha domu:: ',all_text)
    objectbyt.plocha_domu = insert_text
    # Užitná plocha:
    insert_text = find_value('Užitná plocha: ',all_text)
    objectbyt.uzitna_plocha = insert_text
    # Sklep:
    insert_text = find_value('Sklep: ',all_text)
    objectbyt.sklep = insert_text
    # Parkování:
    insert_text = find_value('Parkování: ',all_text)
    objectbyt.parkovani = insert_text
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
    # Energetická náročnost budovy:
    insert_text = find_value('Energetická náročnost budovy: ',all_text)
    objectbyt.energ_narocnost_budovy = insert_text
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
        insert_text[0] = insert_text[0][insert_text[0].find('Prodej bytů')+12:len(insert_text[0])-1]
        insert_text[1] = insert_text[1][insert_text[1].find('Prodej bytů')+12:len(insert_text[1])-1]
        objectbyt.region = insert_text[0]
        objectbyt.subregion = insert_text[1]
    if len(insert_text)==1:
        insert_text[0] = insert_text[0][insert_text[0].find('Prodej bytů ')+12:len(insert_text[0])-1]
        objectbyt.region = insert_text[0]
    #insert_text = elems.text.split('\n')
    #objectbyt.region = insert_text

    # Insert object to DB
    inserted_status = objectbyt.dbinsertDomy()
    return inserted_status

# Function runs at the end of all load - need for close all other that are not actualized
def final_update_byt_prodej(type, script_date_start, connection_config_dict):
    # Input parameter - time of Script start: that to update all rows that are old (were not found now)
    try:
        connection = mysql.connector.connect(**connection_config_dict)
        mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = 'update dbrealtor.' + type + ' set date_close="' + mydatetime + '", status="C" where (date_update < "' \
                + script_date_start + '" AND STATUS !="C") OR (date_open < "' + script_date_start + '" AND date_update IS NULL AND STATUS !="C")'
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Closed OLD objects count: ', row_count)
        logging.info('  Closed OLD objects count: ' + str(cursor.rowcount))
        closed_counts = cursor.rowcount
    except:
        closed_counts = 0
    finally:
        cursor.close()
    return closed_counts

type = 'domy_prodej'
# Define count of all pages based on adds_on_page
adcount = SrealityLibrary.define_pages_count('https://www.sreality.cz/hledani/prodej/domy', driver)
pagescount = int(adcount/adds_on_page) + 1
logging.info('======================= NEW RUN =======================')
logging.info('  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object

# To have ability load only from defined page
skipped_count = 0
failed_count = 0
inserted_count = 0
id_load = 0
closed_counts = 0
counter = 1
try:
    if len(sys.argv) > 1:
        counter = sys.argv[1]
        try:
            counter = int(counter)
        except:
            logging.error('Wrong parameter, not INT')

    # Open Connection
    connection = mysql.connector.connect(**connection_config_dict)
    id_load = SrealityLibrary.start_loading(type, adcount, pagescount,connection)
    while counter <= pagescount:
        link = 'https://www.sreality.cz/hledani/prodej/domy?strana=' + str(counter)
        try:
            advlist = SrealityLibrary.find_all_links(link, 'prodej', driver)
            try:
                if len(advlist) == 0:
                    delay(3)
                    SrealityLibrary.pkill(is_win)
                    continue
            except:
                logging.info('  Skipping: ' + str(link))
                continue
            i = 0
            logging.info('  Page number: ' + str(counter))
            for link in advlist:
                i = i + 1
                # Check whether this object already added
                # is_skipped = check_ad_exist(advert, i, save_path, driver, connection)
                status = find_details_byt_prodej(link, type, id_load, driver, connection)
                if status == 'Skipped':
                    skipped_count = skipped_count + 1
                if status == 'Failed':
                    failed_count = failed_count + 1
                if status == 'Inserted':
                    inserted_count = inserted_count + 1
        except Exception as e:
            logging.info(e)
        finally:
            counter = counter + 1
    closed_counts = final_update_byt_prodej(type, script_date_start, connection_config_dict)
    summary_results = 'Count items: ' + str(adcount) + ';  Count pages: ' + str(pagescount) + ';  Inserted: ' + str(inserted_count) + ';  Skipped: ' + str(skipped_count) + ';  Failed: ' + str(failed_count) + ';  Closed: ' + str(closed_counts)
    logging.info(summary_results)
except Exception as e:
    error_msg = str(e.message) + str(e.args)
    logging.info(error_msg)
finally:
    SrealityLibrary.finish_loading(id_load, adcount, pagescount, inserted_count, skipped_count, failed_count,closed_counts,connection)
    connection.close()
    driver.close()