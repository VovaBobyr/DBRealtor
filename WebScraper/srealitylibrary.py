from selenium import webdriver

#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By

#from selenium.webdriver.chrome.options import Options
#import mysql.connector
#import re
import time
import os
import codecs
import logging
import datetime
from subprocess import call
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

def find_all_links_chrome(link, type, chrome_driver, chromedriver_path, chrome_options):
    prev_link = ''
    links_list = []
    #search_string = 'projekt-detail'
    search_string = 'detail/' + type
    if type == 'projekty':
        search_string = 'projekt-detail'
    # Searching Links
    chrome_driver.get(link)
    #with open('project_page.html', 'w', encoding="utf-8") as f:
    #    f.write(driver.page_source)
    elems = chrome_driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if search_string in elem.get_attribute("href"):
            if elem.get_attribute("href") != prev_link:
                # print(elem.get_attribute("href"))
                links_list.append(elem.get_attribute("href"))
                prev_link = elem.get_attribute("href")

    #if len(links_list) == 0:
    #    # Run FireFox Driver
    #    # It means that page was not loaded till the end, need to run loading through FireFox - it works - temp fix
    #    is_firefox = True
    #    firefox_driver = webdriver.Firefox(executable_path=firefoxdriver_path, options=firefox_options)
    #    firefox_driver.get(link)
    #    # chrome_driver = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)
    #    # chrome_driver.get(link)
    #    all_a = firefox_driver.find_elements_by_xpath('//a[@href]')
    #    links = []
    #    search_string = 'detail/prodej'
    #    cnt = 0
    #    for i in all_a[0:60]:
    #        cnt += 1
    #        if search_string in i.get_attribute("href"):
    #            links.append(i.get_attribute("href"))
    #    # Remove duplicates
    #    links_list = list(set(links))

    ########################## END FireFox driver using ####################################
    return links_list

    # myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
    #elems = chrome_driver.find_elements_by_xpath("//a[@href]")
    #try:
    #    for elem in elems:
    #        if 'detail/prodej' in elem.get_attribute("href"):
    #            if elem.get_attribute("href") != prev_link:
    #                # print(elem.get_attribute("href"))
    #                links_list.append(elem.get_attribute("href"))
    #                prev_link = elem.get_attribute("href")
    #except:
    #    pass
    #finally:
    #    return links_list


def find_all_links_firefox(link, type, firefox_driver, firefoxdriver_path, firefox_options):
    # It means that page was not loaded till the end, need to run loading through FireFox - it works - temp fix

    #driver = webdriver.Firefox(executable_path=gecodriver_path, options=firefox_options)
    firefox_driver.get(link)
    all_a = firefox_driver.find_elements_by_xpath('//a[@href]')
    links = []
    search_string = 'detail/prodej'
    cnt = 0
    for i in all_a[0:55]:
        cnt += 1
        if search_string in i.get_attribute("href"):
            links.append(i.get_attribute("href"))
    # Remove duplicates
    links_list = list(set(links))
    time.sleep(1)
    return links_list


# Fuction to find how many pages are in NEXTs
def define_pages_count(link, driver):
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
    logging.info('  Found advertise count: ' + count_str)
    try:
        count = int(count_str)
    except:
        pass
    return count

# Function for analysing string
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
    sql = "SELECT id FROM dbrealtor." + type + " WHERE obj_number='" + obj_number + "'"
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

def start_loading(type, items_count, pages_count, connection):
    mycursor = connection.cursor()
    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #sql = "INSERT INTO dbrealtor.dataloadlog (type, date_start, status) VALUES('" + type + "', '" + mydatetime + "', 'Open', " +  items_count + ", " + pages_count + ")"
    sql = "INSERT INTO dbrealtor.dataloadlog (type,date_start,status,items_count,pages_count) VALUES('" + str(type) + "', '" + str(mydatetime) + "', 'Open', " + str(items_count) + ", " + str(pages_count) + ")"
    mycursor.execute(sql)
    connection.commit()
    sql = "SELECT MAX(id) FROM dataloadlog"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    for row in result:
        id_load = row[0]
    mycursor.close()
    return id_load

def finish_loading(id_load, items_count, pages_count, inserted_count, skipped_count, failed_count, closed_count, connection):
    mycursor = connection.cursor()
    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "UPDATE dbrealtor.dataloadlog SET date_finish = '" + mydatetime + "', status='Closed', items_count=" + str(items_count) + ", pages_count=" + str(pages_count) + ", inserted_count=" + str(inserted_count) + ", skipped_count=" + str(skipped_count) + ", failed_count=" + str(failed_count) + ", closed_count=" + str(closed_count) + " where id=" + str(id_load)
    mycursor.execute(sql)
    connection.commit()
    mycursor.close()

def find_cena(celcova_cena):
    letters = []
    for i in celcova_cena:
        letters.append(i)
    price_str = ''
    counter = 0
    flag = True
    for i in letters:
        if i == '(':
            flag = False
        if i == ')':
            flag = True
        if i.isdigit() and flag:
            price_str = price_str + i
    try:
        price = int(price_str)
    except:
        price_str = '0'
    return price_str

def pkill(is_win, link):
    if is_win:
        logging.info('  Killing chrome and chromedriver on: ' + link)
        call('Taskkill /IM chrome.exe /F')
        call('Taskkill /IM chromedriver.exe /F')
    else:
        logging.info('  Killing chrome and chromedriver on: ' + link)
        cmd = 'pkill chrome'
        os.system(cmd)
        cmd = 'pkill chromedriver'
        os.system(cmd)

def reopen_driver(link, is_win, driver, chromedriver_path, chrome_options):
    logging.info('  Reopen driver for: ' + link)
    driver.close()
    pkill(is_win, link)
    time.sleep(2)
    driver = webdriver.Chrome(
        executable_path=chromedriver_path,
        options=chrome_options)
    driver.get(link)
    return driver

def start_check_whether_no_scrapping_running():
    pass

