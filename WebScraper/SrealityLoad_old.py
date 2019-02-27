#!/usr/bin/python
import xmlrpc.client

import hashlib
clientId = 19398 # ID klienta
password = '603b3f11131b06e56c2e39dcdb57b30b'
#password = password.encode('utf-8')

key = 'sreality-test' # importni klic
#key = key.encode('utf-8')

''' Take from Admin Panel in CReality '''
def NewSessionId(oldId, password, key):
    varPart = hashlib.md5()
    phrase = oldId + password + key
    phrase = phrase.encode('utf-8')
   #varPart.update(oldId + password + key)
    varPart.update(phrase)
    return oldId[0:48] + varPart.hexdigest()

# Connection to ImportServer
proxy = xmlrpc.client.ServerProxy('http://import.sreality.cz/RPC2/')

#client = xmlrpclib.ServerProxy("http://import.sreality.cz/RPC2")

# Call fuction GetHash to get beggining SessionID
getHash = proxy.getHash(clientId)
if getHash["status"] / 100 == 2:
    # Getting SessionID for next actions
    sessionId = NewSessionId(getHash['output'][0]['sessionId'], password, key)
    # Login to ImportServer
    response = proxy.login(sessionId)
    if response["status"] / 100 == 2:
        print("Logged in.")
        # Putting Ad
        sessionId = NewSessionId(sessionId, password, key)
        advert = {
            "advert_function": 1, # prodej
            "advert_lifetime": 1, # 7 dni
            "advert_price": 10000.0,
            "advert_price_currency": 1, # Kc
            "advert_price_unit": 2, # za mesic
            "advert_type": 1, # byty
            "description": "Pekny byt s vyhledem na zahradu.",
            "locality_city": "Praha",
            "locality_inaccuracy_level": 2, # znepresneni adresy o 1 stupen
            "floor_number": 1, # prvni patro
            "garage": False,
            "loggia": False,
            "balcony": False,
            "terrace": False,
            "ownership": 1, # osobni
            "parking_lots": True,
            "advert_subtype": 4, # Typ bytu 2+kk
            "usable_area": 54, # Plocha bytu 54m^2
            "building_type": 2, # Cihlova budova
            "building_condition": 1, # Stav objektu velmi dobry
            "cellar": True, # Ma sklep
            "heating": (3, 4), # topeni lokalni elektricke a ustredni plynove
            "telecommunication": (1, 2, 4), # telefon, internet, kabelova televize
            "seller_id": 123456,
        }
        #response = client.addAdvert(sessionId, advert)
        response = proxy.listAdvert(sessionId)
        if response["status"] / 100 == 2:
            print('Check successfully.')
            print(response)
        else:
            print("addAdvert: %d %s") % (response["status"], response["statusMessage"])

        # Odhlaseni
        sessionId = NewSessionId(sessionId, password, key)
        proxy.logout(sessionId)
    else:
        print("login: %d %s") % (response["status"], response["statusMessage"])
else:
    print("getHash: %d %s") % (getHash["status"], getHash["statusMessage"])