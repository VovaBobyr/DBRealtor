from mysql.connector import Error
import datetime
import logging
#import time

class ObjectDomyProdejClass:
    """ Main class for Saving object 36 arguments"""
    def __init__(self,id_load,title,description, celkova_cena, poznamka_k_cene, cena, naklady, id_ext, aktualizace, stavba,
                 stav_objektu, vlastnictvi, podlazi,pocet_bytu,plocha_domu,plocha_zastavena,
                 uzitna_plocha,plocha_podlahova,plocha_pozemku,plocha_zahrady,typ_domu,terasa, sklep, datum_nastegovani, rok_kolaudace,
                 rok_reconstrukce, voda, plyn, topeni, odpad, telekomunikace, elektrina, doprava, komunikace,
                 energ_narocnost_budovy, bezbarierovy, vybaveni,bazen,kontakt, link, date_open, umisteni_objektu, parkovani,garaz,puvodni_cena, region, subregion, obj_number, connection):
        """Constructor"""
        self.id_load = id_load
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

    def dbinsertdomy(self):
        try:
            if self.connection.is_connected():
                # Date - today
                mydatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.date_open = mydatetime
                # 35
                objlist = list(self.__dict__.values())
                objlist.pop()
                query = "INSERT INTO dbrealtor.domy_prodej(id_load,title,description,celkova_cena,poznamka_k_cene,cena,naklady,id_ext,aktualizace,stavba,stav_objektu,vlastnictvi," \
                        "podlazi,pocet_bytu,plocha_domu,plocha_zastavena,uzitna_plocha,plocha_podlahova,plocha_pozemku,plocha_zahrady,typ_domu,terasa,sklep,datum_nastegovani,rok_kolaudace,rok_reconstrukce,voda,plyn,topeni,odpad,telekomunikace,elektrina," \
                        "doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vybaveni,bazen,kontakt,link,date_open,umisteni_objektu,parkovani,garaz,puvodni_cena,region,subregion,obj_number)" \
                        " VALUES(" + self.values(objlist) + ")"
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '  Inserted object_number: ', self.obj_number)
                logging.info('  Inserted object_number: %s', self.obj_number)
                cursor.close()
                return 'Inserted'
        except Error as e:
            #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  Error while connecting to MySQL", e)
            logging.error("  Error while connecting to MySQL" + e.msg)
            return 'Failed'
        #finally:
        #    if (self.connection.is_connected()):
        #        self.connection.close()