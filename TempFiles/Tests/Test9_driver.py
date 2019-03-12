from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime


if os.name == 'nt':
    save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
    chromedriver_path = 'C:/Inst/chromedriver.exe'
else:
    save_path = '/opt/dbrealtor/temp/'
    chromedriver_path = '/usr/bin/chromedriver'
chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
    executable_path=chromedriver_path,
    options=chrome_options)
print('OPENED 1st Driver')

link ='https://www.sreality.cz/detail/prodej/byt/1+kk/praha-cast-obce-bubenec-ulice-korunovacni/780705372'
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Get Link1')
driver.get(link)

link='https://www.sreality.cz/detail/prodej/byt/3+kk/praha-cast-obce-ujezd-nad-lesy-ulice-rohoznicka/1235197532'
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Get Link2')
driver.back()
driver.get(link)

link='https://www.sreality.cz/detail/prodej/byt/3+1/liberec-cast-obce-liberec-vi-rochlice--liberec-vi-ulice-zitna/3930562140'
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Get Link3')
driver.back()
driver.get(link)

link='https://www.sreality.cz/detail/prodej/byt/3+kk/liberec-cast-obce-liberec-i-stare-mesto-ulice-sokolska/1051935068'
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Get Link4')
driver.back()
driver.get(link)

link='https://www.sreality.cz/detail/prodej/byt/3+1/praha-cast-obce-nusle-ulice-nezamyslova/22322780'
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Get Link5')
driver.back()
driver.get(link)

driver.close()