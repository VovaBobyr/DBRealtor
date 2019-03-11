from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import requests
#import mysql.connector
#import datetime
#import time

# Windows
#save_path = 'C:/Tmp/'
#path_to_chromedriver ='C:/Inst/chromedriver.exe'

# Linux
save_path = '/opt/dbrealtor/'
path_to_chromedriver ='/usr/bin/chromedriver'

def save_page(page_name, save_path, driver):
    # Part for saving HTML to file
    file_name = 'test.html'
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()

def save_page_get (link, save_path):
    r = requests.get(link)
    file_name = 'test_get.html'
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    open(completeName, 'wb').write(r.content)
    file_object.close()

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
    executable_path=path_to_chromedriver,
    options=chrome_options)

link = 'https://www.google.com.ua'
#link = 'https://www.javascript.com/'
#driver.get(link)
save_page(link, save_path, driver)
#save_page_get(link, save_path)
#driver.close()
