from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import codecs
import mysql.connector
import datetime
import time
import sys
import logging
import SrealityLibrary

# Type:
# 1. Projekty
# - sub-items into each projekt

# First imput parameter is Page from what to start load

# Logging
script_date_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

chrome_options = Options()
chrome_options.add_argument("--headless")

if os.name == 'nt':
    is_win = True
else:
    is_win = False

if is_win:
    save_path = 'C:/Learning/Python/DBRealtor/TempFiles/'
    chromedriver_path = 'C:/Inst/chromedriver.exe'
    log_name = 'C:/Learning/Python/DBRealtor/Logs/SrealityScanner_Projekty_' + script_date_start[:10] + '.log'
else:
    save_path = '/opt/dbrealtor/temp/'
    chromedriver_path = '/usr/bin/chromedriver'
    log_name = '/opt/dbrealtor/Logs/SrealityScanner_Projekty_'+ script_date_start[:10] +'.log'

logging.basicConfig(format = u'[%(asctime)s]  %(message)s',filename=log_name, level=logging.INFO)

# Count of Advertises on page
adds_on_page = 20
delay = 3

driver = webdriver.Chrome(
    executable_path=chromedriver_path,
    options=chrome_options)

connection_config_dict = {
    'user': 'root',
    'password': SrealityLibrary.take_pass(),
    'host': '127.0.0.1',
    'database': 'dbrealtor',
    'raise_on_warnings': True,
    'use_pure': True,
    'autocommit': True,
    'pool_size': 5
}

class ObjectProjektClass:
    """ Main class for Saving object <> arguments"""
    def __init__(self,id_load,link,obj_number,title,region,subregion,date_open,date_update,date_close,status,zahajeni_prodeje,dokonceni_vystavby,k_nastehovani,description,vnitrni_omitky,zaklady,vnitrni_obklady
                 ,fasadni_omitky,stropy,podlahy,okna,dvere,kuchynska_linka,zastavba,zelezobetonove_schodiste,interierove_schodiste,stav_objektu,krytina,umisteni_objektu,strecha,komunikace
                 ,vnejsi_obklady,prevod_do_ov,stavba,vlastnictvi,typ_domu,poloha_domu,kontakt,connection):
        """Constructor"""
        self.id_load = id_load
        self.link = link
        self.obj_number = obj_number
        self.title = title
        self.region = region
        self.subregion = subregion
        self.date_open = date_open
        self.status = 'open'
        self.zahajeni_prodeje = zahajeni_prodeje
        self.dokonceni_vystavby = dokonceni_vystavby
        self.k_nastehovani = k_nastehovani
        self.description = description
        self.vnitrni_omitky = vnitrni_omitky
        self.zaklady = zaklady
        self.vnitrni_obklady = vnitrni_obklady
        self.fasadni_omitky = fasadni_omitky
        self.stropy = stropy
        self.podlahy = podlahy
        self.okna = okna
        self.dvere = dvere
        self.kuchynska_linka = kuchynska_linka
        self.zastavba = zastavba
        self.zelezobetonove_schodiste = zelezobetonove_schodiste
        self.interierove_schodiste = interierove_schodiste
        self.stav_objektu = stav_objektu
        self.krytina = krytina
        self.umisteni_objektu = umisteni_objektu
        self.strecha = strecha
        self.komunikace = komunikace
        self.vnejsi_obklady = vnejsi_obklady
        self.prevod_do_ov = prevod_do_ov
        self.stavba = stavba
        self.vlastnictvi = vlastnictvi
        self.typ_domu = typ_domu
        self.poloha_domu = poloha_domu
        self.kontakt = kontakt
        self.connection = connection

    def values(self, objlist):
        longstr = ""
        for str in objlist:
            longstr = longstr + "'" + str + "'" + ","
        return longstr[0:len(longstr) - 1]

    def dbinsertprojekt(self):
        try:
            if self.connection.is_connected():
                # Date - today
                mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.date_open = mydatetime
                # 35
                objlist = list(self.__dict__.values())
                objlist.pop()
                query = "INSERT INTO dbrealtor.projekty(id_load,link,obj_number,title,region,subregion,date_open,status,zahajeni_prodeje,dokonceni_vystavby,k_nastehovani,description,vnitrni_omitky,zaklady,vnitrni_obklady" \
                        ",fasadni_omitky,stropy,podlahy,okna,dvere,kuchynska_linka,zastavba,zelezobetonove_schodiste,interierove_schodiste,stav_objektu,krytina,umisteni_objektu,strecha,komunikace" \
                        ",vnejsi_obklady,prevod_do_ov,stavba,vlastnictvi,typ_domu,poloha_domu,kontakt)" \
                        " VALUES(" + self.values(objlist) + ")"
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                logging.info('  Inserted project_number: %s', self.obj_number)
                cursor.close()
                return 'Inserted'
        except Exception as e:
            logging.error("  Error while connecting to MySQL" + str(e))
            return 'Failed'

class ObjectProjektClass_Item:
    """ Main class for Saving object 36 arguments"""
    def __init__(self,id_load,proj_number,title,description, celkova_cena, poznamka_k_cene, cena, naklady, id_ext, aktualizace, stavba,
                 stav_objektu, vlastnictvi, podlazi,pocet_bytu,plocha_domu,plocha_zastavena,
                 uzitna_plocha,plocha_podlahova,plocha_pozemku,plocha_zahrady,typ_domu,terasa, sklep, datum_nastegovani, rok_kolaudace,
                 rok_reconstrukce, voda, plyn, topeni, odpad, telekomunikace, elektrina, doprava, komunikace,
                 energ_narocnost_budovy, bezbarierovy, vybaveni,bazen,kontakt, link, date_open, umisteni_objektu, parkovani,garaz,puvodni_cena, region, subregion, obj_number, connection):
        """Constructor"""
        self.id_load = id_load
        self.proj_number = proj_number
        self.title = title
        self.description = description
        self.celkova_cena = celkova_cena
        self.poznamka_k_cene = poznamka_k_cene
        self.cena = cena
        self.naklady = naklady
        self.id_ext = id_ext
        self.aktualizace = aktualizace
        self.stavba = stavba
        self.stav_objektu = stav_objektu
        self.vlastnictvi = vlastnictvi
        self.podlazi = podlazi
        self.pocet_bytu = pocet_bytu
        self.plocha_domu = plocha_domu
        self.plocha_zastavena = plocha_zastavena
        self.uzitna_plocha = uzitna_plocha
        self.plocha_podlahova = plocha_podlahova
        self.plocha_pozemku = plocha_pozemku
        self.plocha_zahrady = plocha_zahrady
        self.typ_domu = typ_domu
        self.terasa = terasa
        self.sklep = sklep
        self.datum_nastegovani = datum_nastegovani
        self.rok_kolaudace = rok_kolaudace
        self.rok_reconstrukce = rok_reconstrukce
        self.voda = voda
        self.plyn = plyn
        self.topeni = topeni
        self.odpad = odpad
        self.telekomunikace = telekomunikace
        self.elektrina = elektrina
        self.doprava = doprava
        self.komunikace = komunikace
        self.energ_narocnost_budovy = energ_narocnost_budovy
        self.bezbarierovy = bezbarierovy
        self.vybaveni = vybaveni
        self.bazen = bazen
        self.kontakt = kontakt
        self.link = link
        self.date_open = date_open
        self.umisteni_objektu = umisteni_objektu
        self.parkovani = parkovani
        self.garaz = garaz
        self.puvodni_cena = puvodni_cena
        self.region = region
        self.subregion = subregion
        self.obj_number = obj_number
        self.connection = connection
    def values(self,objlist):
        longstr = ""
        for str in objlist:
            longstr = longstr + "'" + str + "'" + ","
        return longstr[0:len(longstr) - 1]

    def dbinsertprojekty_items(self):
        try:
            if self.connection.is_connected():
                # Date - today
                mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.date_open = mydatetime
                # 35
                objlist = list(self.__dict__.values())
                objlist.pop()
                query = "INSERT INTO dbrealtor.projekty_items(id_load,proj_number,title,description,celkova_cena,poznamka_k_cene,cena,naklady,id_ext,aktualizace,stavba,stav_objektu,vlastnictvi," \
                        "podlazi,pocet_bytu,plocha_domu,plocha_zastavena,uzitna_plocha,plocha_podlahova,plocha_pozemku,plocha_zahrady,typ_domu,terasa,sklep,datum_nastegovani,rok_kolaudace,rok_reconstrukce,voda,plyn,topeni,odpad,telekomunikace,elektrina," \
                        "doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,bazen,kontakt,link,date_open,umisteni_objektu,parkovani,garaz,puvodni_cena,region,subregion,obj_number)" \
                        " VALUES(" + self.values(objlist) + ")"
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Inserted object_number: ', self.obj_number)
                logging.info('    Inserted object_number: %s', self.obj_number)
                cursor.close()
                return 'Inserted'
        except Exception as e:
            logging.error("  Error while connecting to MySQL" + e.msg)
            return 'Failed'

def find_value(search_string, where):
    return_text = ''
    for line in where:
        if search_string in line:
            return_text = line.replace(search_string,'')
            break
    return  return_text

# Filling deatails for PRODJECT
def filling_details_projekt(link, type, id_load, driver, connection):
    project_number = link[link.rfind('/') + 1:len(link)]
    is_exist = SrealityLibrary.check_ad_exist(project_number, type, connection)
    if is_exist:
        logging.info('  Project with number ' + project_number + ' - SKIPPED')
        #delay=0
        return 'Skipped', project_number
    # Title
    driver.get(link)
    #with open('project.html', 'w', encoding="utf-8") as f:
    #    f.write(driver.page_source)
    try:
        elems = driver.find_element_by_class_name('project-title')
    except:
        try:
            driver.get(link)
            #driver = SrealityLibrary.reopen_driver(link, is_win, driver, chromedriver_path, chrome_options)
            elems = driver.find_element_by_class_name('project-title')
        except:
            logging.info(' 2nd reconnect failed for: ' + link + ' - STOPPING')
            return 'Failed'

    objectproj = ObjectProjektClass('','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)

    #Title
    title = elems.text.replace('\n', '')
    try:
        elems = driver.find_element_by_class_name('location-title')
        title = title + '; ' + elems.text.replace('\n', '')
        objectproj.title = title
    except:
        logging.warn('  WRN: No element <location-title>')

    # Object_Number
    objectproj.obj_number = project_number #link[link.rfind('/') + 1:len(link)]

    # Dates:
    try:
        elems = driver.find_element_by_class_name('project-params')
        all_text = elems.text.split('\n')
        # Zahájení prodeje:
        insert_text = find_value('Zahájení prodeje:', all_text)
        insert_text = insert_text.replace(' ', '')
        objectproj.zahajeni_prodeje = insert_text
        # Zahájení prodeje:
        insert_text = find_value('Dokončení výstavby:', all_text)
        insert_text = insert_text.replace(' ', '')
        objectproj.dokonceni_vystavby = insert_text
        # Zahájení prodeje:
        insert_text = find_value('K nastěhování: ', all_text)
        insert_text = insert_text.replace(' ', '')
        objectproj.k_nastehovani = insert_text
    except:
        logging.warning('  WRN: No element <project-params>')

    # id_load
    objectproj.id_load = str(id_load)
    # Description
    try:
        elems = driver.find_element_by_class_name('description')
        descr_text = elems.text.replace('\n', ' ')
        descr_text = descr_text.replace("'", "")
        objectproj.description = descr_text
    except:
        logging.warning('  WRN: No element <description>')

    # Main block with all details (not title and not kontakt)
    try:
        elems = driver.find_element_by_class_name('params')
        # Processing Params with all details
        all_text = elems.text.split('\n')
        # Základy
        insert_text = find_value('Základy: ', all_text)
        objectproj.zaklady = insert_text
        # Vnitřní obklady:
        insert_text = find_value('Vnitřní obklady: ', all_text)
        objectproj.vnitrni_obklady = insert_text
        # Vnitřní omítky
        insert_text = find_value('Vnitřní omítky: ', all_text)
        objectproj.vnitrni_obklady = insert_text
        # Krytina:
        insert_text = find_value('Krytina: ', all_text)
        objectproj.krytina = insert_text
        # Střecha:
        insert_text = find_value('Střecha: ', all_text)
        objectproj.strecha = insert_text
        # Stropy:
        insert_text = find_value('Stropy: ', all_text)
        objectproj.stropy = insert_text
        # Fasádní omítky:
        insert_text = find_value('Fasádní omítky: ', all_text)
        objectproj.fasadni_omitky = insert_text
        # Podlahy:
        insert_text = find_value('Podlahy: ', all_text)
        objectproj.podlahy = insert_text
        # Vnější obklady:
        insert_text = find_value('Vnější obklady: ', all_text)
        objectproj.vnejsi_obklady = insert_text
        # Železobetonové schodiště:
        insert_text = find_value('Železobetonové schodiště: ', all_text)
        objectproj.zelezobetonove_schodiste = insert_text
        # Dveře:
        insert_text = find_value('Dveře: ', all_text)
        objectproj.dvere = insert_text
        # Kuchyňská linka:
        insert_text = find_value('Kuchyňská linka: ', all_text)
        objectproj.kuchynska_linka = insert_text
        # Okna:
        insert_text = find_value('Okna: ', all_text)
        objectproj.okna = insert_text
        # Interiérové schodiště:
        insert_text = find_value('Interiérové schodiště: ', all_text)
        objectproj.interierove_schodiste = insert_text
        # Zástavba:
        insert_text = find_value('Zástavba: ', all_text)
        objectproj.zastavba = insert_text
        # Poloha domu:
        insert_text = find_value('Poloha domu: ', all_text)
        objectproj.poloha_domu = insert_text
        # Stav objektu:
        insert_text = find_value('Stav objektu: ', all_text)
        objectproj.stav_objektu = insert_text
        # Umístění objektu:
        insert_text = find_value('Umístění objektu: ', all_text)
        objectproj.umisteni_objektu = insert_text
        # Typ domu:
        insert_text = find_value('Typ domu: ', all_text)
        objectproj.typ_domu = insert_text
        # Komunikace:
        insert_text = find_value('Komunikace: ', all_text)
        objectproj.komunikace = insert_text
        # Stavba:
        insert_text = find_value('Stavba: ', all_text)
        objectproj.stavba = insert_text
        # Vlastnictví:
        insert_text = find_value('Vlastnictví: ', all_text)
        objectproj.vlastnictvi = insert_text
    except:
        pass
        #logging.warning('  WRN: No element <params>')

    # Kontakt
    try:
        elems = driver.find_element_by_class_name('contacts')
        insert_text = elems.text.split('\n')
    except:
        pass
        #logging.warning('  WRN: No element <contacts>')
    try:
        full_text = ''
        for txt in insert_text:
            full_text = full_text + txt + ' '
    except:
        pass
    finally:
        objectproj.kontakt = full_text

    # Link
    objectproj.link = link

    # Region and sub-region:
    # it could be that sub-region doesn't exist (exist only for Praha and Brno)
    try:
        elems = driver.find_element_by_class_name('location-title')
        locations = elems.text.split(',')
        for location in locations:
            words = location.split(' ')
            if words[0] == 'ulice':
                sub_region = location
            else:
                region = location.strip()
        objectproj.region = region
        objectproj.subregion = sub_region

    except:
        logging.warning('  WRN: some warning in define location')

    # Insert object to DB
    inserted_status = objectproj.dbinsertprojekt()
    return inserted_status, project_number

# Filling deatails for Item into PRODJECT
def filling_details_projekt_item(link, type, id_load, proj_number, driver, connection):
    obj_number = link[link.rfind('/') + 1:len(link)]
    is_exist = SrealityLibrary.check_ad_exist(obj_number, type, connection)
    if is_exist:
        logging.info('    Object with number ' + obj_number + ' - SKIPPED')
        #delay=0
        return 'Skipped'
    # Title
    driver.get(link)
    #with open('project_item.html', 'w', encoding="utf-8") as f:
    #    f.write(driver.page_source)
    try:
        elems = driver.find_element_by_class_name('property-title')
    except:
        pass
        return 'Failed'

    #38
    objectbyt = ObjectProjektClass_Item('','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',connection)
    #Title
    objectbyt.title = elems.text.replace('\n', '')
    # id_load
    objectbyt.id_load = str(id_load)
    # id_projekt - take from parent projekt running
    objectbyt.proj_number = str(proj_number)
    # Description
    elems = driver.find_element_by_class_name('description')
    descr_text = elems.text.replace('\n',' ')
    descr_text = descr_text.replace("'","")
    objectbyt.description = descr_text

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
    objectbyt.cena = SrealityLibrary.find_cena(objectbyt.celkova_cena)
    # ID zakázky:
    insert_text = find_value('Náklady na bydlení: ',all_text)
    objectbyt.naklady = insert_text
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
    # Terasa:
    insert_text = find_value('Terasa: ',all_text)
    objectbyt.terasa = insert_text
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
    objectbyt.obj_number = obj_number #link[link.rfind('/') + 1:len(link)]
    # Region and sub-region:
    # it could be that sub-region doesn't exist (exist only for Praha and Brno)
    elems = driver.find_element_by_class_name('regions-box')
    insert_text = elems.text.split('\n')
    if len(insert_text) >=2:
        insert_text[0] = insert_text[0][insert_text[0].find('Prodej')+12:len(insert_text[0])-1]
        insert_text[1] = insert_text[1][insert_text[1].find('Prodej')+12:len(insert_text[1])-1]
        objectbyt.region = insert_text[1]
        objectbyt.subregion = insert_text[0]
    if len(insert_text)==1:
        insert_text[0] = insert_text[0][insert_text[0].find('Prodej ')+13:len(insert_text[0])-1]
        objectbyt.region = insert_text[0]
    #insert_text = elems.text.split('\n')
    #objectbyt.region = insert_text

    # Insert object to DB
    inserted_status = objectbyt.dbinsertprojekty_items()
    return inserted_status

def find_links_in_projekt(link, driver):
    prev_link = ''
    links_list = []
    #search_string = 'projekt-detail'
    search_string = 'detail/prodej/'
    # Searching Links
    try:
        driver.get(link)
        #with open('project.html', 'w', encoding="utf-8") as f:
        #    f.write(driver.page_source)
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            if search_string in elem.get_attribute("href"):
                if elem.get_attribute("href") != prev_link:
                    links_list.append(elem.get_attribute("href"))
                    prev_link = elem.get_attribute("href")

        return links_list
    except Exception as e:
        logging.info('  Error: ' + e.message)
        #SrealityLibrary.reopen_driver(link, is_win, driver, chromedriver_path, chrome_options)
        elems = driver.find_elements_by_xpath("//a[@href]")
        try:
            for elem in elems:
                if 'detail/prodej' in elem.get_attribute("href"):
                    if elem.get_attribute("href") != prev_link:
                        # print(elem.get_attribute("href"))
                        links_list.append(elem.get_attribute("href"))
                        prev_link = elem.get_attribute("href")
        except:
            pass
    finally:
        return links_list

# Function runs at the end of all load - need for close all other that are not actualized
def final_update_projekt(type, script_date_start, connection_config_dict):
    # Input parameter - time of Script start: that to update all rows that are old (were not found now)
    try:
        connection = mysql.connector.connect(**connection_config_dict)
        mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = 'update dbrealtor.projekty set date_close="' + mydatetime + '", status="C" where (date_update < "' \
                + script_date_start + '" AND STATUS !="C") OR (date_open < "' + script_date_start + '" AND date_update IS NULL AND STATUS !="C")'
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        logging.info('  Closed old Projekt count: ' + str(cursor.rowcount))
        query = 'update dbrealtor.projekty set date_close="' + mydatetime + '", status="C" where (date_update < "' \
                + script_date_start + '" AND STATUS !="C") OR (date_open < "' + script_date_start + '" AND date_update IS NULL AND STATUS !="C")'
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Closed OLD objects count: ', row_count)
        logging.info('  Closed old Projekt_items count: ' + str(cursor.rowcount))
        closed_counts = cursor.rowcount
    except:
        closed_counts = 0
    finally:
        cursor.close()
    return closed_counts

def all_scrabing_from_page(link, counter, driver):
    skipped_count = 0
    failed_count = 0
    inserted_count = 0
    advlist = SrealityLibrary.find_all_links(link, 'projekty', driver)
    if len(advlist) == 0:
        logging.info('    Advlist = 0: reget link: ' + str(link))
        advlist = SrealityLibrary.find_all_links(link, 'prodej', driver)
        if len(advlist) == 0:
            logging.info('    Advlist = 0: reget failed')
            failed_pages.append(counter)
            status = 'Failed'
            return status, skipped_count, failed_count, inserted_count
    i = 0
    logging.info('  Page number: ' + str(counter))
    for link in advlist:
        i = i + 1
        # Project Part
        # Check whether this object already added
        status, proj_number = filling_details_projekt(link, type_projekty, id_load, driver, connection)
        #if status == 'Skipped':
        #    continue
        projekt_items = find_links_in_projekt(link, driver)

        # Processing items in Project
        if len(projekt_items) == 0:
            logging.info('    Empty items in project')
        for item in projekt_items:
            status = filling_details_projekt_item(item, type_projekty_items, id_load, proj_number, driver, connection)
            if status == 'Skipped':
                skipped_count = skipped_count + 1
            if status == 'Failed':
                failed_count = failed_count + 1
            if status == 'Inserted':
                inserted_count = inserted_count + 1
    status = 'Success'
    return status, skipped_count, failed_count, inserted_count

type_projekty = 'projekty'
type_projekty_items = 'projekty_items'
# Define count of all pages based on adds_on_page
adcount = SrealityLibrary.define_pages_count('https://www.sreality.cz/projekt', driver)
pagescount = int(adcount/adds_on_page) + 1
logging.info('======================= NEW RUN =======================')
logging.info('  Pages count: ' + str(pagescount))
# Main part - go inside to Advertise of each object

# To have ability load only from defined page
skipped_count = 0
failed_count = 0
inserted_count = 0
id_load = 0
closed_counts = 0
counter = 1
failed_pages = []
try:
    if len(sys.argv) > 1:
        counter = sys.argv[1]
        try:
            counter = int(counter)
        except:
            logging.error('Wrong parameter, not INT')

    # Open Connection
    connection = mysql.connector.connect(**connection_config_dict)
    id_load = SrealityLibrary.start_loading(type_projekty, adcount, pagescount,connection)
    while counter <= pagescount:
        link = 'https://www.sreality.cz/projekt?strana=' + str(counter)
        status, skipped_count_1, failed_count_1, inserted_count_1 = all_scrabing_from_page(link, counter, driver)
        skipped_count = skipped_count + skipped_count_1
        failed_count = failed_count + failed_count_1
        inserted_count = inserted_count + inserted_count_1
        counter = counter + 1

    # In case some Pages failed - try to reload it one more time
    if len(failed_pages) > 0:
        for page in failed_pages:
            link = 'https://www.sreality.cz/projekt?strana=' + str(page)
            status, skipped_count_1, failed_count_1, inserted_count_1 = all_scrabing_from_page(link, page, driver)
            skipped_count = skipped_count + skipped_count_1
            failed_count = failed_count + failed_count_1
            inserted_count = inserted_count + inserted_count_1

    closed_counts = final_update_projekt(type_projekty, script_date_start, connection_config_dict)
    summary_results = 'Count items: ' + str(adcount) + ';  Count pages: ' + str(pagescount) + ';  Inserted: ' + str(inserted_count) + ';  Skipped: ' + str(skipped_count) + ';  Failed: ' + str(failed_count) + ';  Closed: ' + str(closed_counts)
    logging.info(summary_results)
except Exception as e:
    #error_msg = str(e.full_msg) + str(e.args)
    logging.info(e)
finally:
    SrealityLibrary.finish_loading(id_load,adcount,pagescount,inserted_count,skipped_count,failed_count,closed_counts,connection)
    connection.close()
    driver.close()