from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
#from mysql.connector import Error
import datetime
import re
import time
#from SrealityScanner_Byty_Prodej_Class import ObjectBytyProdejClass


def take_pass():
    if os.name == 'nt':
        filename = 'c:/inst/info.txt'
    else:
        filename = '/opt/dbrealtor/Backups/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

def save_page(page_name, save_path, link, chromedriver_path, chrome_options):
    # Part for saving HTML to file
    driver = webdriver.Chrome(
        executable_path=chromedriver_path,
        options=chrome_options)
    driver.get(link)
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()
    driver.close()

def find_all_links(link, type, driver):
    prev_link = ''
    links_list = []
    search_string = 'detail/' + type
    # Searching Links
    try:
        #driver = webdriver.Chrome(
        #    executable_path=chromedriver_path,
        #    options=chrome_options)
        print('Driver GET - Find all links')
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
    #print('Driver CLOSED - Find all links')
    #driver.close()

# Fuction to find how many pages are in NEXTs
def define_pages_count(link, driver):
    #try:
    #    driver = webdriver.Chrome(
    #        executable_path=chromedriver_path,
    #        options=chrome_options)
    #    driver.get(link)
    #    print('OPENED driver for Define page count, link: ' + link)
    #except:
    #    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Reconnecting to: ' + link)
    #    driver.get(link)
    print('Driver GET - Define pages count.')
    driver.get(link)
    elems = driver.find_element_by_css_selector(".info.ng-binding")
    #file_name = type + '.html'
    #save_page(file_name,save_path,link,chromedriver_path,chrome_options)
    #file_name = save_path + file_name
    #find_string = 'nalezených'
    all_text = elems.text
    pos1 = all_text.rfind('z celkem')
    pos2 = all_text.rfind('nalezených')
    count_str = all_text[pos1+9:pos2-1]
    count_str = count_str.replace(" ", "")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Found advertise count: ' + count_str)
    try:
        count = int(count_str)
    except:
        pass
    #driver.close()
    #print('Driver CLOSED - Define pages count.')
    return count

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
        connection.commit()
        return True
    mycursor.close()

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


