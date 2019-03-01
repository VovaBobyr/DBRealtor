from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
from mysql.connector import Error
import datetime
import re
import time

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
    def __init__(self, title, typ_bytu, description, celkova_cena, poznamka_k_cene, cena, naklady, id_ext, aktualizace, stavba,
                 stav_objectu, vlastnictvi, podlazi,
                 uzitna_plocha, terasa, sklep, datum_nastegovani, rok_kolaudace,
                 rok_reconstrukce, voda, topeni, odpad, telekomunikace, elektrina, doprava, komunikace,
                 energ_narocnost_budovy, bezbarierovy, vybaveni, vytah, kontakt, link, date_add,umisteni_objektu,parkovani,puvodni_cena,region,subregion,connection):
        """Constructor"""
        self.title = title
        self.typ_bytu = typ_bytu
        self.description = description
        self.celkova_cena = celkova_cena
        self.poznamka_k_cene = poznamka_k_cene
        self.cena = cena
        self.naklady = naklady
        self.id_ext = id_ext
        self.aktualizace = aktualizace
        self.stavba = stavba
        self.stav_objectu = stav_objectu
        self.vlastnictvi = vlastnictvi
        self.podlazi = podlazi
        self.uzitna_plocha = uzitna_plocha
        self.terasa = terasa
        self.sklep = sklep
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
        self.umisteni_objektu = umisteni_objektu
        self.parkovani = parkovani
        self.puvodni_cena = puvodni_cena
        self.region = region
        self.subregion = subregion
        self.connection = connection

    def check_ad_exist(self,obj_number):
        mycursor = self.connection.cursor()
        # query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
        sql = """SELECT id_ext FROM byty WHERE link like '%%%s%%'""" % (obj_number)
        mycursor.execute(sql)
        row_count = len(mycursor.fetchall())
        if row_count == 0:
            return False
        else:
            return True
        mycursor.close()

    def values(self,objlist):
        longstr = ""
        for str in objlist:
            longstr = longstr + "'" + str + "'" + ","
        return longstr[0:len(longstr) - 1]

    def find_cena(self,celcova_cena):
        price_list = re.findall(r'\d+', celcova_cena)
        price_str = ''
        for i in price_list:
            price_str = price_str + i
        #price_int = int(price_str)
        try:
            price = int(price_str)
        except:
            price_str='0'
        return price_str

    def dbinsertbyty(self):
        try:
            #connection = mysql.connector.connect(**connection_config_dict)
            if self.connection.is_connected():
                #db_Info = self.connection.get_server_info()
                #print("Succesfully Connected to MySQL database. MySQL Server version on ", db_Info)

                # Define object_id (latest numbers in link) - check where exist # after number link is
                # example: https://www.sreality.cz/detail/prodej/byt/2+kk/praha-cast-obce-kosire-ulice-plzenska/1409134172
                exist_ending_in_link = link.rfind('#')
                if exist_ending_in_link != -1:
                    ending = exist_ending_in_link
                else:
                    ending = len(self.link)
                obj_number = self.link[self.link.rfind('/') + 1:ending]
                is_exist = self.check_ad_exist(obj_number)
                if is_exist:
                    func_result = 'SKIPPED'
                    print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Object with number ' + obj_number + ' - SKIPPED')
                    return func_result
                else:
                    # Manual update of some fields
                    # Date - today
                    mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.date_add = mydatetime
                    # Cena - based on Celkova cena
                    # Check is_cena_digit?
                    self.cena = self.find_cena(self.celkova_cena)
                    # 35
                    objlist = list(self.__dict__.values())
                    objlist.pop()
                    query = "INSERT INTO dbrealtor.byty(title,typ_bytu,description,celkova_cena,poznamka_k_cene,cena,naklady,id_ext,aktualizace,stavba,stav_objectu,vlastnictvi," \
                            "podlazi,uzitna_plocha,terasa,sklep,datum_nastegovani,rok_kolaudace,rok_reconstrukce,voda,topeni,odpad,telekomunikace,elektrina," \
                            "doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,vytah,kontakt,link,date_add,umisteni_objektu,parkovani,puvodni_cena,region,subregion)" \
                            " VALUES(" + self.values(objlist) + ")"
                    cursor = self.connection.cursor()
                    cursor.execute(query)
                    self.connection.commit()
                    print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Inserted object_number: ', obj_number)
        except Error as e:
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + "  Error while connecting to MySQL", e)
        finally:
            if (self.connection.is_connected()):
                self.connection.close()

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
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        try:
            time.sleep(2)
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Reconnect to take page: ' + link)
            driver.get(link)
            elems = driver.find_element_by_class_name('property-title')
        except:
            print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + ' 2nd reconnect failed for: ' + link + 'STOPPING')
            return
    finally:
        connection = mysql.connector.connect(**connection_config_dict)
    #38
    objectbyt = ObjectBytClass(elems.text.replace('\n',''),'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)

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
adcount = define_pages_count('https://www.sreality.cz/hledani/prodej/byty', 'byty')
pagescount = int(adcount/adds_on_page) + 1
print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object
counter = 0
while counter <= pagescount:
    link = 'https://www.sreality.cz/hledani/prodej/byty?strana=' + str(counter)
    advlist = find_all_advert_links(link)
    counter = counter + 1
    i = 0
    print(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") + '  Page number: ' + str(counter))
    for advert in advlist:
        i = i + 1
        find_details_in_advert(advert, i)
        time.sleep(3)
        pass

driver.close()