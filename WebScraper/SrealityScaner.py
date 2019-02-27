from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from bs4 import BeautifulSoup
#import time
import os
import codecs
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(
    executable_path='C:/Inst/chromedriver.exe',
    options=chrome_options)
save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
#print(driver.find_element_by_id('content').text)
# Count of Advertises on page
adds_on_page = 20


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
    'use_pure': False,
    'autocommit': True,
    'pool_size': 5
}

class ObjectBytClass:
    """ Main class for Saving object 31 arguments"""
    def __init__(self,title,type,description,celkova_cena,poznamka_k_cene,naklady,id_ext,aktualizace,stavba,stav_objectu,vlastnictvi,
                 umisteni_objektu,podlazi,uzitna_plocha,terasa,sklep,parkovani,datum_nastegovani,rok_kolaudace,
                 rok_reconstrukce,voda,topeni,odpad,telekomunikace,elektrina,doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,vytah,kontakt,link,date_add):
        """Constructor"""
        self.title = title
        self.type = type
        self.description = description
        self.celkova_cena = celkova_cena
        self.poznamka_k_cene = poznamka_k_cene
        self.naklady = naklady
        self.id_ext = id_ext
        self.aktualizace = aktualizace
        self.stavba = stavba
        self.stav_objectu = stav_objectu
        self.vlastnictvi= vlastnictvi
        self.podlazi = podlazi
        self.umisteni_objektu = umisteni_objektu
        self.uzitna_plocha = uzitna_plocha
        self.terasa = terasa
        self.sklep = sklep
        self.parkovani = parkovani
        self.datum_nastegovani = datum_nastegovani
        self.rok_kolaudace = rok_kolaudace
        self.rok_reconstrukce = rok_reconstrukce
        self.voda = voda
        self.topeni = topeni
        self.odpad = odpad
        self.telekomunikace = telekomunikace
        self.elektrina = elektrina
        self.doprava = doprava
        self.komunikace = komunikace
        self.energ_narocnost_budovy = energ_narocnost_budovy
        self.bezbarierovy = bezbarierovy
        self.vybaveni = vybaveni
        self.vytah = vytah
        self.kontakt = kontakt
        self.link = link
        self.date_add = date_add
    def dbinsertbyty(self):
        try:
            connection = mysql.connector.connect(**connection_config_dict)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Succesfully Connected to MySQL database. MySQL Server version on ", db_Info)
                mycursor = connection.cursor()
                mycursor.execute('SHOW DATABASES')
                for x in mycursor:
                    print(x)
                #is_exist =
        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if (connection.is_connected()):
                connection.close()

def save_page(page_name):
    # Part for saving HTML to file
    file_name = page_name
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    html = driver.page_source
    file_object.write(html)
    file_object.close()

# Fuction to find how many pages are in NEXTs
def define_pages_count(link, type):
    driver.get(link)
    file_name = type + '.html'

    save_page(file_name)
    file_name = save_path + file_name
    find_string = 'nalezených'
    for str in open(file_name, mode="r", encoding="utf-8"):
        if find_string in str:
            pos1 = str.rfind('<span class="numero ng-binding">')
            pos2 = str.rfind('</span>')
            count_str = str[pos1+32:pos2]
            count_str = count_str.replace(" ", "")
            count = int(count_str)
            print('Found advertise count: ' + count_str)
            break
    return count
    #content = driver.find_elements_by_class_name('.numero.ng-binding')
    #print(content)

#save_page('all_byty.html')

def find_all_advert_links(link):
    prev_link = ''
    links_list = []
    # Searching Links
    driver.get(link)
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if 'detail/prodej' in elem.get_attribute("href"):
            if elem.get_attribute("href") != prev_link:
                #print(elem.get_attribute("href"))
                links_list.append(elem.get_attribute("href"))
                prev_link = elem.get_attribute("href")
    return links_list
    # print(link.text)

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
def find_details_in_advert(link, page_no):
    driver.get(link)
    save_page(str(page_no) + '.html')

    # Title
    elems = driver.find_element_by_class_name('property-title')
    objectbyt = ObjectBytClass(elems.text.replace('\n',''),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','')

    # Description
    elems = driver.find_element_by_class_name('description')
    objectbyt.description = elems.text.replace('\n',' ')

    # Main block with all details (not title and not kontact)
    elems = driver.find_element_by_class_name('params')
    # Processing Params with all details
    all_text = elems.text.split('\n')

    # Celcova cena
    insert_text = find_value('Celková cena: ',all_text)
    objectbyt.celkova_cena = insert_text
    # Poznámka k ceně
    insert_text = find_value('Poznámka k ceně: ',all_text)
    objectbyt.poznamka_k_cene = insert_text
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
    objectbyt.kontakt = insert_text[0] + insert_text[4] + insert_text[5]
    # Link
    objectbyt.link = link

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
#adcount = define_pages_count('https://www.sreality.cz/hledani/prodej/byty', 'byty')
#pagescount = int(adcount/adds_on_page) + 1
#print('Pages count: ' + str(pagescount))
pagescount = 100
# Main part - go inside to Advertise of each object
counter = 1
while counter <= pagescount:
    link = 'https://www.sreality.cz/hledani/prodej/byty?strana=' + str(counter)
    advlist = find_all_advert_links(link)
    counter += counter
    i = 0
    for advert in advlist:
        i = i + 1
        find_details_in_advert(advert, i)


driver.close()

