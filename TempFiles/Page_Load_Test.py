'''
 Script for test environment:
 1. Check chromedriver
 2. Check that HTML files is saved
 3. Check connection to DB (mySQL)
'''
import codecs
import time

import mysql.connector
from selenium import webdriver

from selenium.webdriver.chrome.options import Options as Option_Chrome
from selenium.webdriver.firefox.options import Options as Option_Firefox

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
import datetime
import requests
from selenium import webdriver

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

def inicialize_chromedriver():
    pass

def inicialize_geckodriver():
    pass

def test_chrome_webdriver(input,driver):
    #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':   OPENED 1st Driver')

    link ='https://www.sreality.cz/hledani/prodej/byty?strana=' + str(input)
    driver.get(link)
    with open('page.html', 'w+', encoding='utf-8') as f:
        f.write(driver.page_source)
        f.close()
    elems = driver.find_elements_by_xpath("//a[@href]")
    count = str(len(elems))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': Test #' + str(input) + '; Count of HREF: ' + count)

    search_string = 'detail/prodej'
    links_list = []
    prev_link = ''

    for elem in elems:
        if search_string in elem.get_attribute("href"):
            if elem.get_attribute("href") != prev_link:
                links_list.append(elem.get_attribute("href"))
                prev_link = elem.get_attribute("href")

    print('Count: ' + str(len(links_list)))

def test_chrome_webdriver_new(input, driver):
    link = 'https://www.sreality.cz/hledani/prodej/byty?strana=' + str(input)
    driver.get(link)
    WebDriverWait(driver, timeout=10)
    links = []
    with open('screenshot.png', 'w+') as f:
        driver.save_screenshot(f)
        f.close()

    all_a = driver.find_elements_by_xpath('//a[@href]')
    element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-layout"]/div[2]/div[2]/div[4]/div/div/div/div/div[3]/div/div[22]')))

    ids = driver.find_elements_by_xpath('//*[@id="page-layout"]/div[2]/div[2]/div[4]/div/div/div/div/div[3]/div/div[22]')
    for id in ids:
        if id.get_attribute("href"):
            links.append()

    search_string = 'detail/prodej'
    cnt = 0

    for i in all_a[0:55]:
        cnt += 1
        if search_string in i.get_attribute("href"):
            links.append(i.get_attribute("href"))
    # Remove duplicates
    removed_list = list(set(links))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': Test #' + str(input) + '; FullList: '+ str(len(links)) + ' Count of unique HREFs: ' + str(len(removed_list)))

def test_firefox_webdriver(input,driver):

    #driver= webdriver.Firefox(executable_path=gecodriver_path, options=options_firefox)
    link = 'https://www.sreality.cz/hledani/prodej/byty?strana=' + str(input)
    driver.get(link)
    all_a = driver.find_elements_by_xpath('//a[@href]')
    links = []
    search_string = 'detail/prodej'
    cnt = 0

    for i in all_a[0:55]:
        cnt += 1
        if search_string in i.get_attribute("href"):
            links.append(i.get_attribute("href"))
    # Remove duplicates
    removed_list = list(set(links))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': Test #' + str(input) + '; FullList: '+ str(len(links)) + ' Count of unique HREFs: ' + str(len(removed_list)))
    time.sleep(5)
    #driver.quit()

##################### Chrome ##############################
if os.name == 'nt':
    save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
    chromedriver_path = 'C:/Inst/chromedriver.exe'
    gecodriver_path = 'C:/Inst/geckodriver.exe'
else:
    save_path = '/opt/dbrealtor/temp/'
    chromedriver_path = '/usr/bin/chromedriver'

options_chrome = Option_Chrome()
options_chrome.add_argument("--headless")

options_firefox = Option_Firefox()
-options_firefox.add_argument("--headless")

#driver_chrome = webdriver.Chrome(executable_path=chromedriver_path,options=options_chrome)
driver_gecko = webdriver.Firefox(executable_path=gecodriver_path, options=options_firefox)

for i in range(1,200): test_firefox_webdriver(i, driver_gecko)
#for i in range(61,103): test_chrome_webdriver_new(i, driver_chrome)

#driver_chrome.close()
driver_gecko.close()

##################### FireFox ##############################
#driver_firefox = webdriver.Firefox()

