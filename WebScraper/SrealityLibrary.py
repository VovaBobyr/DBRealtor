from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
#from mysql.connector import Error
import datetime
import re
import time
from SrealityScanner_Byty_Prodej_Class import ObjectBytyProdejClass
from SrealityScanner_Byty_Pronajem_Class import ObjectBytPronajemClass

def take_pass():
    filename = 'c:/inst/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

def save_page(page_name, save_path, driver):
    # Part for saving HTML to file
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()

def find_all_links(link, type, driver):
    prev_link = ''
    links_list = []
    search_string = 'detail/' + type
    # Searching Links
    try:
        driver.get(link)
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            if search_string in elem.get_attribute("href"):
                if elem.get_attribute("href") != prev_link:
                    # print(elem.get_attribute("href"))
                    links_list.append(elem.get_attribute("href"))
                    prev_link = elem.get_attribute("href")
        return links_list
    except:
        try:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Reconnect to for Find_All_Details: ' + link)
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
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  BAD connection for Find_All_Details: ' + link)

# Fuction to find how many pages are in NEXTs
def define_pages_count(link, type, save_path, driver):
    try:
        driver.get(link)
    except:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Reconnecting to: ' + link)
        driver.get(link)
    file_name = type + '.html'
    save_page(file_name,save_path,driver)
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

            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Found advertise count: ' + count_str)
            break

    return count
    #content = driver.find_elements_by_class_name('.numero.ng-binding')
    #print(content)

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

def check_ad_exist(obj_number, type, connection):
    mycursor = connection.cursor()
    # query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
    sql = "SELECT id_ext FROM dbrealtor." + type + " WHERE obj_number='" + obj_number + "'"
    mycursor.execute(sql)
    row_count = len(mycursor.fetchall())
    if row_count == 0:
        return False
    else:
        # If exist - need to update column Date_Update:
        mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = 'update dbrealtor.' + type + ' set date_update="' + mydatetime + '", status="U", date_close=NULL where obj_number="' + obj_number + '"'
        mycursor.execute(query)
        #connection.commit()
        return True
    #mycursor.close()

def find_cena(celcova_cena):
    price_list = re.findall(r'\d+', celcova_cena)
    price_str = ''
    for i in price_list:
        price_str = price_str + i
    # price_int = int(price_str)
    try:
        price = int(price_str)
    except:
        price_str = '0'
    return price_str


# Big part to find details in HTML
def find_details_byt_prodej(link, page_no, save_path, type, driver, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = check_ad_exist(obj_number, type, connection)
    if is_exist:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Object with number ' + obj_number + ' - SKIPPED')
        delay=0
        return 'SKIPPED'
    else:
        driver.get(link)
        save_page(str(page_no) + '.html',save_path, driver)
    # Title
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' 2nd reconnect failed for: ' + link + ' - STOPPING')
            return
    #finally:
    #    connection = mysql.connector.connect(**connection_config_dict)
    #38
    objectbyt = ObjectBytyProdejClass(elems.text.replace('\n',''),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)

    # Description
    elems = driver.find_element_by_class_name('description')
    objectbyt.description = elems.text.replace('\n',' ')

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
    objectbyt.cena = find_cena(objectbyt.celkova_cena)
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

def find_details_byt_pronajem(link, page_no, save_path, type, driver, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = check_ad_exist(obj_number, type, connection)
    if is_exist:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Object with number ' + obj_number + ' - SKIPPED')
        delay=0
        return 'SKIPPED'
    else:
        driver.get(link)
        save_page(str(page_no) + '.html',save_path, driver)
    # Title
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' 2nd reconnect failed for: ' + link + ' - STOPPING')
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
    objectbyt.cena = find_cena(objectbyt.celkova_cena)
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


    #property_title = driver.find_element_by_xpath("//div[@class='property-title']")
    #print(property_title)
    #for elem in elems:
    #    if 'detail/prodej' in elem.get_attribute("href"):
    #        if elem.get_attribute("href") != prev_link:
    #            print(elem.get_attribute("href"))
    #            links_list.append(elem.get_attribute("href"))
    #            prev_link = elem.get_attribute("href")


# Function runs at the end of all load - need for close all other that are not actualized
def final_update_byt_prodej(type, script_date_start, connection):
    # Input parameter - time of Script start: that to update all rows that are old (were not found now)
    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = 'update dbrealtor.' + type + ' set date_close="' + mydatetime + '", status="C" where date_update < "'\
            + script_date_start + '" OR (date_open < "' + script_date_start + '" AND date_update IS NULL)'
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    row_count = len(cursor.fetchall())
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Closed OLD objects count: ', row_count)
    cursor.close()

def final_update_byt_pronajem(type, script_date_start, connection):
    # Input parameter - time of Script start: that to update all rows that are old (were not found now)
    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = 'update dbrealtor.' + type + ' set date_close="' + mydatetime + '", status="C" where date_update < "'\
            + script_date_start + '" OR (date_open < "' + script_date_start + '" AND date_update IS NULL)'
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    row_count = len(cursor.fetchall())
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Closed OLD objects count: ', row_count)
    cursor.close()