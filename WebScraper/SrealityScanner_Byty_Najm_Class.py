#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#import os
#import codecs
#import mysql.connector
from mysql.connector import Error
import datetime
import re
#import time

class ObjectBytNajmClass:
    """ Main class for Saving object 36 arguments"""
    def __init__(self, title, typ_bytu, description, celkova_cena, poznamka_k_cene, cena, naklady, id_ext, aktualizace, stavba,
                 stav_objectu, vlastnictvi, podlazi,
                 uzitna_plocha, terasa, sklep, datum_nastegovani, rok_kolaudace,
                 rok_reconstrukce, voda, topeni, odpad, telekomunikace, elektrina, doprava, komunikace,
                 energ_narocnost_budovy, bezbarierovy, vybaveni, vytah, kontakt, link, date_open, umisteni_objektu, parkovani, puvodni_cena, region, subregion, obj_number, connection):
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
        self.date_open = date_open
        self.umisteni_objektu = umisteni_objektu
        self.parkovani = parkovani
        self.puvodni_cena = puvodni_cena
        self.region = region
        self.subregion = subregion
        self.obj_number = obj_number
        self.connection = connection

    def check_ad_exist(self,obj_number,connection):
        mycursor_check = self.connection.cursor()
        # query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
        sql = """SELECT id_ext FROM byty WHERE link like '%%%s%%'""" % (obj_number)
        mycursor_check.execute(sql)
        row_count = len(mycursor_check.fetchall())
        mycursor_check.close()
        if row_count == 0:
            return False
        else:
            return True

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
            if self.connection.is_connected():
                # Date - today
                mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.date_open = mydatetime
                # Cena - based on Celkova cena
                # Check is_cena_digit?
                self.cena = self.find_cena(self.celkova_cena)
                # 35
                objlist = list(self.__dict__.values())
                objlist.pop()
                query = "INSERT INTO dbrealtor.byty_najm(title,typ_bytu,description,celkova_cena,poznamka_k_cene,cena,naklady,id_ext,aktualizace,stavba,stav_objectu,vlastnictvi," \
                        "podlazi,uzitna_plocha,terasa,sklep,datum_nastegovani,rok_kolaudace,rok_reconstrukce,voda,topeni,odpad,telekomunikace,elektrina," \
                        "doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,vytah,kontakt,link,date_open,umisteni_objektu,parkovani,puvodni_cena,region,obj_number,subregion)" \
                        " VALUES(" + self.values(objlist) + ")"
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Inserted object_number: ', self.obj_number)
                cursor.close()
        except Error as e:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  Error while connecting to MySQL", e)
        #finally:
        #    if (self.connection.is_connected()):
        #        self.connection.close()