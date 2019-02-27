class ObjectBytClass:
    """ Main class for Saving object 31 arguments"""
    def __init__(self,title,type,description,celkova_cena,poznamka_k_cene,naklady,id_ext,aktualizace,stavba,stav_objectu,vlastnictvi,
                 umisteni_objektu,podlazi,uzitna_plocha,terasa,sklep,parkovani,datum_nastegovani,rok_kolaudace,
                 rok_reconstrukce,voda,topeni,odpad,telekomunikace,elektrina,doprava,komunikace,energ_narocnost_budovy,bezbarierovy,vebaveni,vytah,kontakt,link):
        """Constructor"""
        self.title = title
        self.type = type
        self.description = description
        self.celkova_cena = celkova_cena
        self.poznamka_k_cene = poznamka_k_cene
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
        self.vebaveni = vebaveni
        self.vytah = vytah
        self.kontakt = kontakt
        self.link = link

objectbyt = ObjectBytClass('1' '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '','')
mylist = list(objectbyt.__dict__.values())
pass