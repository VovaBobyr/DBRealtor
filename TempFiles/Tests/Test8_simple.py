import requests
import os
import codecs

# Windows
#save_path = 'C:/Tmp/'
# Linux
save_path = '/opt/dbrealtor/'

def save_page_get (link, save_path):
    r = requests.get(link)
    file_name = 'test_get.html'
    completeName = os.path.join(save_path, file_name)
    file_object = codecs.open(completeName, "w", "utf-8")
    open(completeName, 'wb').write(r.content)
    file_object.close()

link = 'https://www.sreality.cz'
#link = 'https://www.javascript.com/'
#driver.get(link)
#save_page(link, save_path, driver)
save_page_get(link, save_path)
#driver.close()
