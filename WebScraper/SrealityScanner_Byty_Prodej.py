from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
#from mysql.connector import Error
import datetime
#import re
import time
from SrealityScanner_Byty_Prodej_Class import ObjectBytClass

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
driver = webdriver.Chrome(
    executable_path='C:/Inst/chromedriver.exe',
    options=chrome_options)
save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
#print(driver.find_element_by_id('content').text)
# Count of Advertises on page
adds_on_page = 20
delay = 3


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

def save_page(page_name):
    # Part for saving HTML to file
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()

def check_ad_exist(obj_number,connection):
    mycursor = connection.cursor()
    # query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
    sql = "SELECT id_ext FROM byty WHERE obj_number='" + obj_number + "'"
    mycursor.execute(sql)
    row_count = len(mycursor.fetchall())
    if row_count == 0:
        return False
    else:
        # If exist - need to update column Date_Update:
        mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = 'update dbrealtor.byty set date_update="' + mydatetime + '", status="U" where obj_number="' + obj_number + '"'
        mycursor.execute(query)
        #connection.commit()
        return True
    #mycursor.close()

# Fuction to find how many pages are in NEXTs
def define_pages_count(link, type):
    try:
        driver.get(link)
    except:
        print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Reconnecting to: ' + link)
        driver.get(link)
    file_name = type + '.html'
    save_page(file_name)
    file_name = save_path + file_name
    find_string = 'nalezených'
    for str in open(file_name, mode="r", encoding="utf-8"):
        if find_string in str:
            pos1 = str.rfind('<span class="numero ng-binding">')
            pos2 = str.rfind('</span>')
            count_str = str[pos1 + 32:pos2]
            count_str = count_str.replace(" ", "")
            count_str = count_str.replace(" ", "")
            count = int(count_str)

            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Found advertise count: ' + count_str)
            break

    return count
    #content = driver.find_elements_by_class_name('.numero.ng-binding')
    #print(content)

#save_page('all_byty.html')

def find_all_advert_links(link):
    prev_link = ''
    links_list = []
    # Searching Links
    try:
        driver.get(link)
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            if 'detail/prodej' in elem.get_attribute("href"):
                if elem.get_attribute("href") != prev_link:
                    # print(elem.get_attribute("href"))
                    links_list.append(elem.get_attribute("href"))
                    prev_link = elem.get_attribute("href")
        return links_list
    except:
        try:
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Reconnect to for Find_All_Details: ' + link)
            driver.get(link)
            elems = driver.find_elements_by_xpath("//a[@href]")
            for elem in elems:
                if 'detail/prodej' in elem.get_attribute("href"):
                    if elem.get_attribute("href") != prev_link:
                        # print(elem.get_attribute("href"))
                        links_list.append(elem.get_attribute("href"))
                        prev_link = elem.get_attribute("href")
            return links_list
        except:
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  BAD connection for Find_All_Details: ' + link)

# Function for analysing string -
def string_analyzer_byt(str, objectbyt):
    """Analysing string to define to what property to insert"""
    return objectbyt

def find_value(search_string, where):
    return_text = ''
    for line in where:
        if search_string in line:
            return_text = line.replace(search_string,'')
            break
    return  return_text

# Big part to find details in HTML
def find_details_in_advert(link, page_no, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = check_ad_exist(obj_number, connection)
    if is_exist:
        print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Object with number ' + obj_number + ' - SKIPPED')
        delay=0
        return 'SKIPPED'
    else:
        driver.get(link)
        save_page(str(page_no) + '.html')
    # Title
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + ' 2nd reconnect failed for: ' + link + ' - STOPPING')
            return
    #finally:
    #    connection = mysql.connector.connect(**connection_config_dict)
    #38
    objectbyt = ObjectBytClass(elems.text.replace('\n',''),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)

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
    # Cena - define from Celcova cana into Object
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
    objectbyt.stav_objectu = insert_text
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
    objectbyt.dbinsertbyty()


    #property_title = driver.find_element_by_xpath("//div[@class='property-title']")
    #print(property_title)
    #for elem in elems:
    #    if 'detail/prodej' in elem.get_attribute("href"):
    #        if elem.get_attribute("href") != prev_link:
    #            print(elem.get_attribute("href"))
    #            links_list.append(elem.get_attribute("href"))
    #            prev_link = elem.get_attribute("href")

# Define count of all pages based on adds_on_page
adcount = define_pages_count('https://www.sreality.cz/hledani/prodej/byty', 'byty_prodej')
pagescount = int(adcount/adds_on_page) + 1
print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object
counter = 0
# Open Connection and cursor
connection = mysql.connector.connect(**connection_config_dict)
while counter <= pagescount:
    link = 'https://www.sreality.cz/hledani/prodej/byty?strana=' + str(counter)
    advlist = find_all_advert_links(link)
    counter = counter + 1
    i = 0
    print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Page number: ' + str(counter))
    for advert in advlist:
        i = i + 1
        # Check whether this object already added
        is_skipped = find_details_in_advert(advert, i, connection)
        if is_skipped == 'SKIPPED':
            delay = 0
        else:
            delay = 3
        time.sleep(delay)
connection.close()
driver.close()