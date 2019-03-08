#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#import os
#import codecs
#import mysql.connector
from mysql.connector import Error
import datetime
import re
#import time

class ObjectBytPronajemClass:
    """ Main class for Saving object 34 arguments"""
    def __init__(self, title,obj_number,date_open,status,cena,celkova_cena,poznamka_k_cene,puvodni_cena,description,link,region,subregion,
                aktualizace,id_ext,stavba,stav_objektu,vlastnictvi,umisteni_objektu,podlazi,uzitna_plocha,terasa,sklep,voda,topeni,plyn,odpad,telekomunikace,
                elektrina,doprava,komunikace,vybaveni,kontakt,connection):
        """Constructor"""
        self.title = title
        self.obj_number = obj_number
        self.date_open = date_open
        self.status = status
        self.cena = cena
        self.celkova_cena = celkova_cena
        self.poznamka_k_cene = poznamka_k_cene
        self.puvodni_cena = puvodni_cena
        self.description = description
        self.link = link
        self.region = region
        self.subregion = subregion
        self.aktualizace = aktualizace
        self.id_ext = id_ext
        self.stavba = stavba
        self.stav_objektu = stav_objektu
        self.vlastnictvi = vlastnictvi
        self.umisteni_objektu = umisteni_objektu
        self.podlazi = podlazi
        self.uzitna_plocha = uzitna_plocha
        self.terasa = terasa
        self.sklep = sklep
        self.voda = voda
        self.topeni = topeni
        self.plyn = plyn
        self.odpad = odpad
        self.telekomunikace = telekomunikace
        self.elektrina = elektrina
        self.doprava = doprava
        self.komunikace = komunikace
        self.vybaveni = vybaveni
        self.kontakt = kontakt
        self.connection = connection

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
                # 35
                objlist = list(self.__dict__.values())
                objlist.remove(self.connection)
                #connection2 = objlist.pop()
                query = "INSERT INTO dbrealtor.byty_pronajem(title,obj_number,date_open,status,cena,celkova_cena,poznamka_k_cene,puvodni_cena,description,link,region,subregion," \
                        "aktualizace,id_ext,stavba,stav_objektu,vlastnictvi,umisteni_objektu,podlazi,uzitna_plocha,terasa,sklep,voda,topeni,plyn,odpad,telekomunikace," \
                        "elektrina,doprava,komunikace,vybaveni,kontakt)" \
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