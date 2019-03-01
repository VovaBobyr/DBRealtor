import os
#import codecs
import mysql.connector
from mysql.connector import Error
import datetime

def take_pass():
    filename = 'c:/inst/info.txt'
    text = open(filename, mode="r", encoding="utf-8")
    line = text.readline()
    return line

class ObjectBytClass:
    """ Main class for Saving object 31 arguments"""

    def __init__(self, title, typ_bytu, description, celkova_cena, poznamka_k_cene, cena, naklady, id_ext, aktualizace, stavba,
                 stav_objectu, vlastnictvi, podlazi,
                 uzitna_plocha, terasa, sklep, datum_nastegovani, rok_kolaudace,
                 rok_reconstrukce, voda, topeni, odpad, telekomunikace, elektrina, doprava, komunikace,
                 energ_narocnost_budovy, bezbarierovy, vybaveni, vytah, kontakt, link, date_add,umisteni_objektu,parkovani):
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

# Check whether exist or not this object in DB
def check_ad_exist(obj_number, connection):
    mycursor = connection.cursor()
    #query = """SELECT id_ext FROM byty WHERE link like '%%s%'""" % (obj_number)
    sql = """SELECT id_ext FROM byty WHERE link like '%%%s%%'""" % (obj_number)
    mycursor.execute(sql)
    row_count = len(mycursor.fetchall())
    mycursor.close()
    if row_count == 0:
        return False
    else:
        return True

def values(objlist):
    longstr = ""
    for str in objlist:
        longstr = longstr + "'" + str +"'" + ","
    return longstr[0:len(longstr)-1]

def dbinsertbyty(objlist):
    #try:
    connection = mysql.connector.connect(**connection_config_dict)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Succesfully Connected to MySQL database. MySQL Server version on ", db_Info)
        link = 'https://www.sreality.cz/detail/prodej/byt/2+kk/praha-cast-obce-kosire-ulice-plzenska/1111111'
        # Define object_id (latest numbers in link) - check where exist # after number link is
        # example: https://www.sreality.cz/detail/prodej/byt/2+kk/praha-cast-obce-kosire-ulice-plzenska/1409134172
        exist_ending_in_link = link.rfind('#')
        if exist_ending_in_link != -1:
            ending = exist_ending_in_link
        else:
            ending = len(link)
        obj_number = link[link.rfind('/') + 1:ending]
        is_exist = check_ad_exist(obj_number, connection)
        if is_exist:
            func_result = 'SKIPPED'
            print('Object with number ----- ' + obj_number + ' ------ skipped')
            return func_result
        else:
            # 34
            query = "INSERT INTO dbrealtor.byty(title,typ_bytu,description,celkova_cena,poznamka_k_cene,cena,naklady,id_ext,aktualizace,stavba,stav_objectu,vlastnictvi," \
                    "podlazi,uzitna_plocha,terasa,sklep,datum_nastegovani,rok_kolaudace,rok_reconstrukce,voda,topeni,odpad,telekomunikace,elektrina," \
                    "doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,vytah,kontakt,link,date_add,umisteni_objektu,parkovani)" \
                    " VALUES(" + values(objlist) + ")"
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            print('Inserted object_number: ', obj_number)

    #except Error as e:
    #    print("Error while connecting to MySQL", e)
    #finally:
    if (connection.is_connected()):
        connection.close()

datetime = datetime.datetime.now().strftime("%Y%m%d")
objectbyt = ObjectBytClass('1', '2', '3', '4', '5', 0, '7', '8', '9', '10',
                           '11', '12', '13', '14', '15', '16','17', '18', '19', '20',
                           '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                           '31','32',datetime, '34', '35')
objlist = list(objectbyt.__dict__.values())

dbinsertbyty(objlist)
