from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
import datetime
import time


link = "https://www.sreality.cz/hledani/prodej/byty"
# print("Inside link: " + link_page)
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
#driver = webdriver.Chrome("C:/Inst/chromedriver.exe", options=chrome_options)

save_path = "/opt/dbrealtor/TempFiles"
#save_path = "C:/Learning/Python/DBRealtor/dbrealtor/TempFiles"

def save_page(save_path, driver):
    # Part for saving HTML to file
    file_name = '01,html'
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()

save_page(save_path, driver)