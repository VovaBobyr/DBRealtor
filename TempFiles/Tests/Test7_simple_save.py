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

def save_page(page_name, save_path, driver, link):
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    driver.get(link)
    html = driver.page_source
    file_object.write(html)
    file_object.close()


chrome_options = Options()
chrome_options.add_argument("--headless")
#driver = webdriver.Chrome(
#    executable_path='C:/Inst/chromedriver.exe',
#    options=chrome_options)

driver = webdriver.Chrome(
    executable_path=path_to_chromedriver,
    options=chrome_options)

link = 'https://www.sreality.cz'
#link = 'https://www.javascript.com/'
#driver.get(link)
save_page('test_new.html', save_path, driver, link)
#save_page_get(link, save_path)
#driver.close()
